"""Recommend service configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "recommend-service"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_recommend"
    read_database_url: str | None = None

    # Redis
    redis_url: str = "redis://localhost:6379/2"

    # Recommendation
    default_top_k: int = 10
    recommend_cache_ttl: int = 180

    # AB Testing
    ab_enabled: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8004

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
