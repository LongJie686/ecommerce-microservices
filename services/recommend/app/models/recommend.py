"""Recommend service ORM models."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Index, Integer, Float
from shared.database import Base


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Integer(primary_key=True, autoincrement=True)
    user_id = Integer(nullable=False, index=True)
    product_id = Integer(nullable=False, index=True)
    behavior_type = String(20, nullable=False)  # view, click, cart, purchase, rate
    score = Float(default=1.0)  # view=1, click=2, cart=3, purchase=5, rate=4
    created_at = DateTime(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_behavior_user_product", "user_id", "product_id"),
        Index("ix_behavior_type", "behavior_type"),
    )


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Integer(primary_key=True, autoincrement=True)
    user_id = Integer(nullable=False, index=True)
    product_id = Integer(nullable=False)
    score = Float(default=0.0)
    strategy = String(50, default="hybrid")  # cf, content, hot, hybrid
    ab_group = String(10, default="A")
    created_at = DateTime(default=datetime.utcnow)

    __table_args__ = (
        Index("ix_rec_user_strategy", "user_id", "strategy"),
    )


class ABTestConfig(Base):
    __tablename__ = "ab_test_configs"

    id = Integer(primary_key=True, autoincrement=True)
    name = String(100, nullable=False)
    strategy_a = String(50, nullable=False)
    strategy_b = String(50, nullable=False)
    ratio = Float(default=0.5)  # A:B ratio
    is_active = Integer(default=1)
    created_at = DateTime(default=datetime.utcnow)
