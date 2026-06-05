"""Shared service-level singletons for crawler service."""
from app.config import settings
from shared.cache import RedisClient
from shared.database import DatabaseManager
from shared.mq import KafkaProducer

db = DatabaseManager(write_url=settings.database_url)
redis = RedisClient(url=settings.redis_url)
kafka = KafkaProducer(settings.kafka_bootstrap_servers) if settings.kafka_bootstrap_servers else None
