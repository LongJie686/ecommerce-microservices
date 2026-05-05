"""Product service ORM models - demonstrates read/write splitting and Redis caching."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Text, Index, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from shared.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Integer(primary_key=True, autoincrement=True)
    name = String(100, nullable=False)
    parent_id = Integer(ForeignKey("categories.id"), nullable=True)
    sort_order = Integer(default=0)
    created_at = DateTime(default=datetime.utcnow)

    products = relationship("Product", back_populates="category")

    __table_args__ = (
        Index("ix_categories_parent_id", "parent_id"),
    )


class Product(Base):
    __tablename__ = "products"

    id = Integer(primary_key=True, autoincrement=True)
    name = String(200, nullable=False)
    category_id = Integer(ForeignKey("categories.id"), nullable=False, index=True)
    price = Numeric(10, 2, nullable=False)
    original_price = Numeric(10, 2, nullable=True)
    description = Text(default="")
    image_url = String(500, default="")
    stock = Integer(default=0)
    sales_count = Integer(default=0)
    rating = Numeric(3, 1, default=Decimal("0.0"))
    source = String(50, default="")  # jd, taobao
    source_url = String(500, default="")
    status = Integer(default=1)  # 1=on_sale, 0=off_sale
    is_deleted = Integer(default=0, nullable=False)  # logical deletion: 0=normal, 1=deleted
    created_at = DateTime(default=datetime.utcnow)
    updated_at = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="products")

    __table_args__ = (
        Index("ix_products_category_status", "category_id", "status"),
        Index("ix_products_sales", "sales_count"),
        Index("ix_products_price", "price"),
        # Covering index: list hot products query only needs status + sales_count + name/price,
        # so this index covers the filter + sort + select columns without table lookup
        Index("ix_products_covering_hot", "status", "sales_count", "name", "price"),
    )
