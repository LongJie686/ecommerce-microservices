"""User service configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "user-service"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_user"
    read_database_url: str | None = None

    # Auth
    jwt_secret: str = "change-me-in-production"
    jwt_expire_hours: int = 24

    # Server
    host: str = "0.0.0.0"
    port: int = 8002

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
