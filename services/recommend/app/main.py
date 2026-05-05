"""Recommend service - handles recommendation algorithms and AB testing."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from shared.cache import RedisClient
from app.config import settings
from app.routers import recommend as recommend_router

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)
redis = RedisClient(url=settings.redis_url)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.recommend import UserBehavior, Recommendation, ABTestConfig  # noqa: F401
    db.init_tables()
    await redis.connect()
    yield
    await redis.close()


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


app.include_router(recommend_router.router, prefix="/api/recommend", tags=["recommend"])
