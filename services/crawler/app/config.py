"""Crawler service configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "crawler-service"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_crawler"

    # Redis
    redis_url: str = "redis://localhost:6379/3"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "crawler-results"

    # Crawler settings
    max_concurrent_tasks: int = 5
    request_timeout: int = 30

    # Server
    host: str = "0.0.0.0"
    port: int = 8005

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
