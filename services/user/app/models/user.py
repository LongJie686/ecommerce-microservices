"""User service ORM models - demonstrates MySQL table design, indexes, transactions."""
from __future__ import annotations

from datetime import datetime, timezone

def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy import Column, String, DateTime, Text, Index, ForeignKey, Integer
from sqlalchemy.orm import relationship

from shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nickname = Column(String(100), default="")
    avatar = Column(String(500), default="")
    status = Column(Integer, default=1)  # 1=active, 0=disabled
    is_deleted = Column(Integer, default=0, nullable=False)  # logical deletion: 0=normal, 1=deleted
    created_at = Column(DateTime, default=_utcnow)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_username_status", "username", "status"),
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(20), nullable=False, default="user")  # user, admin

    user = relationship("User", back_populates="roles")

    __table_args__ = (
        Index("ix_user_roles_user_id", "user_id"),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(Integer, nullable=True)  # 0=female, 1=male
    preferred_categories = Column(Text, default="")  # comma-separated category IDs
    price_range = Column(String(20), default="0-99999")  # e.g. "100-500"
    tags = Column(Text, default="")  # user preference tags, comma-separated
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow)

    user = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("ix_user_profiles_user_id", "user_id"),
    )
