"""Schemas for crawler service."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CrawlStartRequest(BaseModel):
    platform: str = Field(..., pattern="^(jd|taobao)$")
    keyword: str = Field(..., min_length=1, max_length=200)


class CrawlTaskResponse(BaseModel):
    id: int
    platform: str
    keyword: str
    status: str
    total_count: int
    success_count: int

    model_config = {"from_attributes": True}
