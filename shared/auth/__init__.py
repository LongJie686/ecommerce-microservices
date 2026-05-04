"""JWT authentication utilities."""

from __future__ import annotations

import time
from typing import Any

import jwt


def create_token(payload: dict[str, Any], secret: str, expires_in: int = 3600 * 24) -> str:
    payload = {**payload, "exp": time.time() + expires_in, "iat": time.time()}
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_token(token: str, secret: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])
