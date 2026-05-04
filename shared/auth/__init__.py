"""JWT authentication utilities."""

from __future__ import annotations

import time
from typing import Any

import jwt


def create_token(payload: dict[str, Any], secret: str, expire_hours: int = 24) -> str:
    data = {**payload, "exp": time.time() + expire_hours * 3600, "iat": time.time()}
    return jwt.encode(data, secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])
