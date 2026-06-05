"""Shared service-level singletons for product service."""
from app.config import settings
from shared.cache import RedisClient
from shared.database import DatabaseManager

db = DatabaseManager(write_url=settings.database_url, read_url=settings.read_database_url)
redis = RedisClient(url=settings.redis_url)
