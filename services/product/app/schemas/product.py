"""Request/Response schemas for product service."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str = Field(..., max_length=200)
    category_id: int
    price: Decimal
    original_price: Decimal | None = None
    description: str = ""
    image_url: str = ""
    stock: int = 0
    source: str = ""
    source_url: str = ""


class ProductUpdate(BaseModel):
    name: str | None = None
    price: Decimal | None = None
    description: str | None = None
    stock: int | None = None
    status: int | None = None


class ProductResponse(BaseModel):
    id: int
    name: str
    category_id: int
    price: Decimal
    original_price: Decimal | None
    description: str
    image_url: str
    stock: int
    sales_count: int
    rating: Decimal
    source: str
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}


class CategoryResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None
    sort_order: int

    model_config = {"from_attributes": True}
