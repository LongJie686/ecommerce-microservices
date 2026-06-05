"""Request/Response schemas for recommend service."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BehaviorRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)
    behavior_type: Literal["view", "click", "cart", "purchase", "rate"]


class RecommendRequest(BaseModel):
    user_id: int = Field(..., gt=0)
    top_k: int = Field(default=10, ge=1, le=50)
    strategy: Literal["cf", "content", "hot", "hybrid"] = "hybrid"
