"""Gateway service configuration."""
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "gateway-service"
    debug: bool = False

    # Database (for rate limiting counters)
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce"

    # Redis (for rate limiting + blacklisting)
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    jwt_secret: str = ""

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

    @field_validator("jwt_secret")
    @classmethod
    def jwt_secret_must_be_strong(cls, v: str) -> str:
        if not v:
            raise ValueError("JWT_SECRET environment variable must be set")
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters")
        return v


settings = Settings()
