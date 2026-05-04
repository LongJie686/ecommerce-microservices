"""Product service configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "product-service"
    debug: bool = False

    # Database (read/write splitting)
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_product"
    read_database_url: str | None = None

    # Redis
    redis_url: str = "redis://localhost:6379/1"

    # Cache TTL
    product_cache_ttl: int = 300
    category_cache_ttl: int = 600

    # Server
    host: str = "0.0.0.0"
    port: int = 8003

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
