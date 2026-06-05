"""Crawler service ORM models."""
from __future__ import annotations

from datetime import datetime, timezone

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
from decimal import Decimal

from sqlalchemy import Column, String, DateTime, Text, Index, Integer, Numeric
from shared.database import Base


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    platform = Column(String(20), nullable=False)  # jd, taobao
    keyword = Column(String(200), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    fail_count = Column(Integer, default=0)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    __table_args__ = (
        Index("ix_crawl_task_status", "status"),
    )


class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, nullable=False, index=True)
    platform = Column(String(20), nullable=False)
    product_name = Column(String(200), nullable=False)
    price = Column(Numeric(10, 2), default=Decimal("0.0"))
    original_price = Column(Numeric(10, 2), nullable=True)
    sales_count = Column(Integer, default=0)
    rating = Column(Numeric(3, 1), default=Decimal("0.0"))
    shop_name = Column(String(200), default="")
    product_url = Column(String(500), default="")
    image_url = Column(String(500), default="")
    category = Column(String(100), default="")
    description = Column(Text, default="")
    raw_data = Column(Text, default="")
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_crawl_result_task", "task_id"),
        Index("ix_crawl_result_platform", "platform"),
    )
