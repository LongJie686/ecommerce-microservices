"""Recommend service ORM models."""
from __future__ import annotations

from datetime import datetime, timezone

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy import Column, String, DateTime, Index, Integer, Float, CheckConstraint
from shared.database import Base


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False, index=True)
    behavior_type = Column(String(20), nullable=False)  # view, click, cart, purchase, rate
    score = Column(Float, default=1.0)  # view=1, click=2, cart=3, purchase=5, rate=4
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_behavior_user_product", "user_id", "product_id"),
        Index("ix_behavior_type", "behavior_type"),
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    product_id = Column(Integer, nullable=False)
    score = Column(Float, default=0.0)
    strategy = Column(String(50), default="hybrid")  # cf, content, hot, hybrid
    ab_group = Column(String(10), default="A")
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        Index("ix_rec_user_strategy", "user_id", "strategy"),
    )


class ABTestConfig(Base):
    __tablename__ = "ab_test_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    strategy_a = Column(String(50), nullable=False)
    strategy_b = Column(String(50), nullable=False)
    ratio = Column(Float, default=0.5)  # A group ratio, must be in (0, 1) exclusive
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=_utcnow)

    __table_args__ = (
        CheckConstraint("ratio > 0 AND ratio < 1", name="ck_ab_ratio_range"),
    )
