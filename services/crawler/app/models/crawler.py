"""Crawler service ORM models."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Text, Index, Integer, Numeric
from shared.database import Base


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id = Integer(primary_key=True, autoincrement=True)
    platform = String(20, nullable=False)  # jd, taobao
    keyword = String(200, nullable=False)
    status = String(20, default="pending")  # pending, running, completed, failed
    total_count = Integer(default=0)
    success_count = Integer(default=0)
    fail_count = Integer(default=0)
    error_message = Text(default="")
    created_at = DateTime(default=datetime.utcnow)
    updated_at = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_crawl_task_status", "status"),
    )


class CrawlResult(Base):
    __tablename__ = "crawl_results"

    id = Integer(primary_key=True, autoincrement=True)
    task_id = Integer(nullable=False, index=True)
    platform = String(20, nullable=False)
    product_name = String(200, nullable=False)
    price = Numeric(10, 2, default=Decimal("0.0"))
    original_price = Numeric(10, 2, nullable=True)
    sales_count = Integer(default=0)
    rating = Numeric(3, 1, default=Decimal("0.0"))
    shop_name = String(200, default="")
    product_url = String(500, default="")
    image_url = String(500, default="")
    category = String(100, default="")
    description = Text(default="")
    raw_data = Text(default="")
    created_at = DateTime(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_crawl_result_task", "task_id"),
        Index("ix_crawl_result_platform", "platform"),
    )
