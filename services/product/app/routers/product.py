"""Product API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import db, redis
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.product_service import ProductService, CategoryService

router = APIRouter()

product_svc = ProductService(redis, cache_ttl=settings.product_cache_ttl)
category_svc = CategoryService(redis, cache_ttl=settings.category_cache_ttl)


def get_write_session():
    yield from db.get_write_session()


def get_read_session():
    yield from db.get_read_session()


@router.post("")
def create_product(req: ProductCreate, session: Session = Depends(get_write_session)):
    return product_svc.create_product(session, req)


@router.get("")
async def list_products(
    category_id: int | None = None,
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_read_session),
):
    return await product_svc.list_products(session, category_id, keyword, page, page_size)


@router.get("/hot")
async def hot_products(limit: int = Query(default=10, ge=1, le=100), session: Session = Depends(get_read_session)):
    return await product_svc.get_hot_products(session, limit)


@router.get("/{product_id}")
async def get_product(product_id: int, session: Session = Depends(get_read_session)):
    return await product_svc.get_product(session, product_id)


@router.put("/{product_id}")
async def update_product(product_id: int, req: ProductUpdate, session: Session = Depends(get_write_session)):
    return await product_svc.update_product(session, product_id, req)


@router.get("/categories/all")
async def list_categories(session: Session = Depends(get_read_session)):
    return await category_svc.list_categories(session)
