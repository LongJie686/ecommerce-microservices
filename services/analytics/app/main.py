"""Analytics service - handles data analysis and visualization APIs."""
from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from app.config import settings
from app.routers import analytics as analytics_router

app = FastAPI(title=settings.service_name, version="1.0.0")
app.add_middleware(TracingMiddleware)

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)


@app.on_event("startup")
async def startup():
    from app.models.analytics import PriceStats, SalesTrend, ShopRanking  # noqa: F401
    db.init_tables()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


app.include_router(analytics_router.router, prefix="/api/analytics", tags=["analytics"])
