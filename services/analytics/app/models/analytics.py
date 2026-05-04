"""Analytics service ORM models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Index, Integer, Float
from shared.database import Base


class PriceStats(Base):
    __tablename__ = "price_stats"

    id = Integer(primary_key=True, autoincrement=True)
    category = String(100, nullable=False)
    price_min = Float(default=0.0)
    price_max = Float(default=0.0)
    price_avg = Float(default=0.0)
    price_median = Float(default=0.0)
    product_count = Integer(default=0)
    calculated_at = DateTime(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_price_stats_category", "category"),
    )


class SalesTrend(Base):
    __tablename__ = "sales_trends"

    id = Integer(primary_key=True, autoincrement=True)
    date = String(10, nullable=False)  # YYYY-MM-DD
    category = String(100, default="")
    total_sales = Integer(default=0)
    total_revenue = Float(default=0.0)
    product_count = Integer(default=0)
    created_at = DateTime(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_sales_trend_date", "date"),
    )


class ShopRanking(Base):
    __tablename__ = "shop_rankings"

    id = Integer(primary_key=True, autoincrement=True)
    platform = String(20, nullable=False)
    shop_name = String(200, nullable=False)
    product_count = Integer(default=0)
    avg_rating = Float(default=0.0)
    total_sales = Integer(default=0)
    calculated_at = DateTime(default=datetime.utcnow)
