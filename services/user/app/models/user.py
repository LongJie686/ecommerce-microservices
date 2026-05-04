"""User service ORM models - demonstrates MySQL table design, indexes, transactions."""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, DateTime, Text, Index, ForeignKey, Integer
from sqlalchemy.orm import relationship

from shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Integer(primary_key=True, autoincrement=True)
    username = String(50, unique=True, nullable=False, index=True)
    password_hash = String(255, nullable=False)
    nickname = String(100, default="")
    avatar = String(500, default="")
    status = Integer(default=1)  # 1=active, 0=disabled
    created_at = DateTime(default=datetime.utcnow)
    updated_at = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_username_status", "username", "status"),
    )


class UserRole(Base):
    __tablename__ = "user_roles"

    id = Integer(primary_key=True, autoincrement=True)
    user_id = Integer(ForeignKey("users.id"), nullable=False)
    role = String(20, nullable=False, default="user")  # user, admin

    user = relationship("User", back_populates="roles")

    __table_args__ = (
        Index("ix_user_roles_user_id", "user_id"),
    )


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Integer(primary_key=True, autoincrement=True)
    user_id = Integer(ForeignKey("users.id"), unique=True, nullable=False)
    age = Integer(nullable=True)
    gender = Integer(nullable=True)  # 0=female, 1=male
    preferred_categories = Text(default="")  # comma-separated category IDs
    price_range = String(20, default="0-99999")  # e.g. "100-500"
    tags = Text(default="")  # user preference tags, comma-separated
    updated_at = DateTime(default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")

    __table_args__ = (
        Index("ix_user_profiles_user_id", "user_id"),
    )
