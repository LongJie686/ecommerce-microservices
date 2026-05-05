"""Gateway service - API gateway with auth, rate limiting, circuit breaker, and routing."""
from contextlib import asynccontextmanager
import time
import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from shared.tracing import TracingMiddleware
from shared.auth import verify_token
from shared.cache import RedisClient
from app.config import settings

logger = logging.getLogger(__name__)

redis = RedisClient(url=settings.redis_url)


class CircuitBreaker:
    """Circuit breaker pattern: protects downstream services from cascading failure.

    States: CLOSED (normal) -> OPEN (tripped, reject all) -> HALF_OPEN (probe)
    Trips when failure count exceeds threshold within a time window.
    """

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self._failure_count: dict[str, int] = {}
        self._state: dict[str, str] = {}  # "closed", "open", "half_open"
        self._last_failure_time: dict[str, float] = {}

    def is_available(self, service: str) -> bool:
        state = self._state.get(service, "closed")
        if state == "closed":
            return True
        if state == "open":
            elapsed = time.time() - self._last_failure_time.get(service, 0)
            if elapsed >= self.recovery_timeout:
                self._state[service] = "half_open"
                return True
            return False
        return True  # half_open: allow one probe request

    def record_success(self, service: str) -> None:
        self._failure_count[service] = 0
        self._state[service] = "closed"

    def record_failure(self, service: str) -> None:
        count = self._failure_count.get(service, 0) + 1
        self._failure_count[service] = count
        self._last_failure_time[service] = time.time()
        if count >= self.failure_threshold:
            self._state[service] = "open"
            logger.warning("Circuit breaker OPEN for %s after %d failures", service, count)

    @property
    def state_summary(self) -> dict:
        return {svc: self._state.get(svc, "closed") for svc in self._state}


circuit_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=30)

SERVICE_MAP = {
    "/api/users": settings.user_service_url,
    "/api/products": settings.product_service_url,
    "/api/categories": settings.product_service_url,
    "/api/search": settings.product_service_url,
    "/api/recommend": settings.recommend_service_url,
    "/api/ab-test": settings.recommend_service_url,
    "/api/crawler": settings.crawler_service_url,
    "/api/analytics": settings.analytics_service_url,
}

PUBLIC_PATHS = {"/health", "/api/users/login", "/api/users/register"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis.connect()
    yield
    await redis.close()


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(request: Request, path: str):
    full_path = f"/{path}"

    # Auth check for non-public paths
    if not any(full_path.startswith(p) or full_path == p for p in PUBLIC_PATHS):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(status_code=401, content={"code": 401, "message": "Missing token"})
        try:
            verify_token(auth_header[7:], settings.jwt_secret)
        except Exception:
            return JSONResponse(status_code=401, content={"code": 401, "message": "Invalid token"})

    # Rate limiting: atomic sliding window via Redis Lua script
    trace_id = request.headers.get("X-Trace-ID", "anonymous")
    rate_key = f"rate:{trace_id}"
    window_script = """
    local current = redis.call("INCR", KEYS[1])
    if current == 1 then
        redis.call("EXPIRE", KEYS[1], ARGV[1])
    end
    return current
    """
    count = await redis._client.eval(window_script, 1, rate_key, "60")
    if count > settings.rate_limit_rpm:
        return JSONResponse(status_code=429, content={"code": 429, "message": "Rate limit exceeded"})

    # Route to target service
    target_url = None
    target_prefix = None
    for prefix, service_url in SERVICE_MAP.items():
        if full_path.startswith(prefix):
            target_url = service_url + full_path
            target_prefix = prefix
            break

    if not target_url:
        return JSONResponse(status_code=404, content={"code": 404, "message": "Service not found"})

    # Circuit breaker check
    if not circuit_breaker.is_available(target_prefix):
        return JSONResponse(status_code=503, content={
            "code": 503, "message": f"Service {target_prefix} temporarily unavailable (circuit open)"
        })

    # Forward request with circuit breaker tracking
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = dict(request.headers)
            headers.pop("host", None)
            resp = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=await request.body(),
                params=dict(request.query_params),
            )
        if resp.status_code >= 500:
            circuit_breaker.record_failure(target_prefix)
        else:
            circuit_breaker.record_success(target_prefix)
        return JSONResponse(status_code=resp.status_code, content=resp.json())
    except (httpx.ConnectError, httpx.TimeoutException) as e:
        circuit_breaker.record_failure(target_prefix)
        logger.error("Service %s connection failed: %s", target_prefix, str(e))
        return JSONResponse(status_code=502, content={
            "code": 502, "message": f"Service unavailable: {target_prefix}"
        })
