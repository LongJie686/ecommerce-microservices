"""Gateway service configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "gateway-service"
    debug: bool = False

    # Database (for rate limiting counters)
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce"

    # Redis (for rate limiting + blacklisting)
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = "change-me-in-production"

    # Rate limiting
    rate_limit_rpm: int = 60
    rate_limit_burst: int = 10

    # Service URLs
    user_service_url: str = "http://localhost:8002"
    product_service_url: str = "http://localhost:8003"
    recommend_service_url: str = "http://localhost:8004"
    crawler_service_url: str = "http://localhost:8005"
    analytics_service_url: str = "http://localhost:8006"

    # Server
    host: str = "0.0.0.0"
    port: int = 8001

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
