"""User service configuration."""
from __future__ import annotations

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = "user-service"
    debug: bool = False

    # Database
    database_url: str = "mysql+pymysql://root:root123@localhost:3306/ecommerce_user"
    read_database_url: str | None = None

    # Auth
    jwt_secret: str = ""
    jwt_expire_hours: int = 24

    # Server
    host: str = "0.0.0.0"
    port: int = 8002

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
