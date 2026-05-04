"""Unified API response format."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse


def success(data: Any = None, message: str = "ok", code: int = 200) -> dict:
    return {"code": code, "message": message, "data": data}


def error(message: str, code: int = 400, data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}


def paginated(data: list, total: int, page: int, page_size: int, message: str = "ok") -> dict:
    return {
        "code": 200,
        "message": message,
        "data": data,
        "pagination": {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        },
    }


class ApiResponse(JSONResponse):
    def __init__(self, content: Any = None, code: int = 200, message: str = "ok", status_code: int = 200):
        super().__init__(
            status_code=status_code,
            content={"code": code, "message": message, "data": content},
        )
