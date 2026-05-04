"""Crawler service - handles data crawling and Kafka messaging."""
from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from shared.cache import RedisClient
from app.config import settings

app = FastAPI(title=settings.service_name, version="1.0.0")
app.add_middleware(TracingMiddleware)

db = DatabaseManager(write_url=settings.database_url)
redis = RedisClient(url=settings.redis_url)


@app.on_event("startup")
async def startup():
    db.init_tables()
    await redis.connect()


@app.on_event("shutdown")
async def shutdown():
    await redis.close()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


# from app.routers import task, status
# app.include_router(task.router, prefix="/api/crawler", tags=["crawler"])
