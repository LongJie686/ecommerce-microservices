"""Analytics API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import db
from app.services.analytics_service import AnalyticsService

router = APIRouter()
svc = AnalyticsService()


def get_read_session():
    yield from db.get_read_session()


@router.get("/dashboard")
def dashboard(session: Session = Depends(get_read_session)):
    return svc.dashboard(session)


@router.get("/price-distribution")
def price_distribution(category: str | None = None, session: Session = Depends(get_read_session)):
    return svc.price_distribution(session, category)


@router.get("/sales-trend")
def sales_trend(
    category: str | None = None,
    days: int = Query(default=7, ge=1, le=365),
    session: Session = Depends(get_read_session),
):
    return svc.sales_trend(session, category, days)


@router.get("/shop-comparison")
def shop_comparison(platform: str | None = None, session: Session = Depends(get_read_session)):
    return svc.shop_comparison(session, platform)
