"""Shared service-level singletons for analytics service."""
from app.config import settings
from shared.database import DatabaseManager

db = DatabaseManager(write_url=settings.database_url, read_url=settings.read_database_url)
