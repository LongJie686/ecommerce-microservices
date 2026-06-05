"""Analytics service ORM models."""
from __future__ import annotations

from datetime import datetime, timezone

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy import Column, String, DateTime, Index, Integer, Float
from shared.database import Base


class PriceStats(Base):
    __tablename__ = "price_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(100), nullable=False)
    price_min = Column(Float, default=0.0)
    price_max = Column(Float, default=0.0)
    price_avg = Column(Float, default=0.0)
    price_median = Column(Float, default=0.0)
    product_count = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_price_stats_category", "category"),
    )


class SalesTrend(Base):
    __tablename__ = "sales_trends"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    category = Column(String(100), default="")
    total_sales = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    product_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_sales_trend_date", "date"),
    )


class ShopRanking(Base):
    __tablename__ = "shop_rankings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False)
    shop_name = Column(String(200), nullable=False)
    product_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    total_sales = Column(Integer, default=0)
    calculated_at = Column(DateTime, default=_utcnow)
