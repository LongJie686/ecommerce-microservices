"""Analytics request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel


class DashboardResponse(BaseModel):
    product_overview: dict
    category_distribution: list[dict]
    top_sales: list[dict]


class PriceDistributionResponse(BaseModel):
    distribution: list[dict]
    total: int
    avg: float


class SalesTrendResponse(BaseModel):
    trend: list[dict]


class ShopComparisonResponse(BaseModel):
    shops: list[dict]
