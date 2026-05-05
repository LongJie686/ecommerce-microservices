"""Analytics service - handles data analysis and visualization APIs."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from app.config import settings
from app.routers import analytics as analytics_router

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.analytics import PriceStats, SalesTrend, ShopRanking  # noqa: F401
    db.init_tables()
    yield


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


app.include_router(analytics_router.router, prefix="/api/analytics", tags=["analytics"])
