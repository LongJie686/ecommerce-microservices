"""Request/Response schemas for user service."""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    nickname: str = Field("", max_length=100)


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    age: int | None = None
    gender: int | None = None
    preferred_categories: str | None = None
    price_range: str | None = None
    tags: str | None = None


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    avatar: str
    status: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ProfileResponse(BaseModel):
    user_id: int
    age: int | None
    gender: int | None
    preferred_categories: str
    price_range: str
    tags: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    token: str
    user: UserResponse
