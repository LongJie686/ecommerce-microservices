"""Crawler service - handles data crawling and Kafka messaging."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from app.config import settings
from app.dependencies import db, redis, kafka


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.crawler import CrawlTask, CrawlResult  # noqa: F401
    db.init_tables()
    await redis.connect()
    if kafka:
        await kafka.start()
    yield
    await redis.close()
    if kafka:
        await kafka.stop()


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


from app.routers import crawler as crawler_router  # noqa: E402
app.include_router(crawler_router.router, prefix="/api/crawler", tags=["crawler"])
