"""Gateway service - API gateway with auth, rate limiting, and routing."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import httpx

from shared.tracing import TracingMiddleware
from shared.auth import verify_token
from shared.cache import RedisClient
from app.config import settings

redis = RedisClient(url=settings.redis_url)

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

    # Rate limiting via Redis
    trace_id = request.headers.get("X-Trace-ID", "anonymous")
    rate_key = f"rate:{trace_id}"
    count = await redis.get(rate_key)
    if count and int(count) > settings.rate_limit_rpm:
        return JSONResponse(status_code=429, content={"code": 429, "message": "Rate limit exceeded"})
    current = int(count or 0) + 1
    await redis.set(rate_key, str(current), expire=60)

    # Route to target service
    target_url = None
    for prefix, service_url in SERVICE_MAP.items():
        if full_path.startswith(prefix):
            target_url = service_url + full_path
            break

    if not target_url:
        return JSONResponse(status_code=404, content={"code": 404, "message": "Service not found"})

    # Forward request
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = dict(request.headers)
        headers.pop("host", None)
        resp = await client.request(
            method=request.method,
            url=target_url,
            headers=headers,
            content=await request.body(),
            params=dict(request.query_params),
        )
        return JSONResponse(status_code=resp.status_code, content=resp.json())
