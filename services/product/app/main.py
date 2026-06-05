"""Product service - handles product CRUD, search, and caching."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from app.config import settings
from app.dependencies import db, redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.product import Product, Category  # noqa: F401
    db.init_tables()
    await redis.connect()
    yield
    await redis.close()


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


from app.routers import product as product_router  # noqa: E402
app.include_router(product_router.router, prefix="/api/products", tags=["product"])
