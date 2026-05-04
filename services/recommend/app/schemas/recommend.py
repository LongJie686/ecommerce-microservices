"""Request/Response schemas for recommend service."""
from __future__ import annotations

from pydantic import BaseModel


class BehaviorRequest(BaseModel):
    user_id: int
    product_id: int
    behavior_type: str  # view, click, cart, purchase, rate


class RecommendRequest(BaseModel):
    user_id: int
    top_k: int = 10
    strategy: str = "hybrid"  # cf, content, hot, hybrid
