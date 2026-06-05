"""Recommend API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import db, redis
from app.schemas.recommend import BehaviorRequest, RecommendRequest
from app.services.recommend_service import RecommendService

router = APIRouter()
svc = RecommendService(redis, cache_ttl=settings.recommend_cache_ttl)


def get_write_session():
    yield from db.get_write_session()


def get_read_session():
    yield from db.get_read_session()


@router.post("/behavior")
def record_behavior(req: BehaviorRequest, session: Session = Depends(get_write_session)):
    return svc.record_behavior(session, req)


@router.post("")
async def get_recommendations(req: RecommendRequest, session: Session = Depends(get_write_session)):
    return await svc.get_recommendations(session, req)


@router.get("/{user_id}/history")
def get_history(user_id: int, strategy: str | None = None,
                session: Session = Depends(get_read_session)):
    return svc.get_history(session, user_id, strategy)
