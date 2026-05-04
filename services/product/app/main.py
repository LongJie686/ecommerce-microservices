"""Product service - handles product CRUD, search, and caching."""
from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from shared.cache import RedisClient
from app.config import settings

app = FastAPI(title=settings.service_name, version="1.0.0")
app.add_middleware(TracingMiddleware)

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)
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


# from app.routers import product, category, search
# app.include_router(product.router, prefix="/api/products", tags=["product"])
# app.include_router(category.router, prefix="/api/categories", tags=["category"])
# app.include_router(search.router, prefix="/api/search", tags=["search"])
