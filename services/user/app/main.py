"""User service - handles user registration, login, and profiles."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from app.config import settings
from app.routers import user as user_router

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models.user import User, UserRole, UserProfile  # noqa: F401
    db.init_tables()
    yield


app = FastAPI(title=settings.service_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(TracingMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


app.include_router(user_router.router, prefix="/api/users", tags=["user"])
