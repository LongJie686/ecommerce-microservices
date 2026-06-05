"""User API routes - controller layer, only handles request/response."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import db
from app.schemas.user import RegisterRequest, LoginRequest, ProfileUpdateRequest
from app.services.user_service import UserService

router = APIRouter()
svc = UserService()


def get_write_session():
    yield from db.get_write_session()


def get_read_session():
    yield from db.get_read_session()


@router.post("/register")
def register(req: RegisterRequest, session: Session = Depends(get_write_session)):
    return svc.register(session, req.username, req.password, req.nickname)


@router.post("/login")
def login(req: LoginRequest, session: Session = Depends(get_write_session)):
    return svc.login(session, req.username, req.password,
                     jwt_secret=settings.jwt_secret,
                     jwt_expire_hours=settings.jwt_expire_hours)


@router.get("/{user_id}")
def get_user(user_id: int, session: Session = Depends(get_read_session)):
    return svc.get_profile(session, user_id)


@router.put("/{user_id}/profile")
def update_profile(user_id: int, req: ProfileUpdateRequest, session: Session = Depends(get_write_session)):
    return svc.update_profile(session, user_id, req)


@router.get("")
def list_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_read_session),
):
    return svc.list_users(session, page, page_size)
