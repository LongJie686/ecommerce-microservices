"""User service - handles user registration, login, and profiles."""
from fastapi import FastAPI
from shared.tracing import TracingMiddleware
from shared.database import DatabaseManager
from app.config import settings

app = FastAPI(title=settings.service_name, version="1.0.0")
app.add_middleware(TracingMiddleware)

db = DatabaseManager(
    write_url=settings.database_url,
    read_url=settings.read_database_url,
)


@app.on_event("startup")
async def startup():
    db.init_tables()


@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.service_name}


# Register routers after implementing Phase 2
# from app.routers import user, profile
# app.include_router(user.router, prefix="/api/users", tags=["user"])
# app.include_router(profile.router, prefix="/api/profiles", tags=["profile"])
