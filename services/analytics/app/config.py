"""Analytics service configuration."""
from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "analytics-service"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_analytics"
    read_database_url: str | None = None

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_consumer_group: str = "analytics-group"

    # Server
    host: str = "0.0.0.0"
    port: int = 8006

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
