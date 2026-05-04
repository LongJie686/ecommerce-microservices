"""Product data access layer - reads from slave, writes to master."""
from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.product import Product, Category


class ProductRepo:
    @staticmethod
    def create(session: Session, **kwargs) -> Product:
        product = Product(**kwargs)
        session.add(product)
        session.flush()
        return product

    @staticmethod
    def get_by_id(session: Session, product_id: int) -> Product | None:
        return session.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def update(session: Session, product_id: int, **kwargs) -> Product | None:
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None
        for key, value in kwargs.items():
            if value is not None and hasattr(product, key):
                setattr(product, key, value)
        session.flush()
        return product

    @staticmethod
    def list_products(session: Session, category_id: int | None = None,
                      keyword: str | None = None, page: int = 1,
                      page_size: int = 20) -> tuple[list[Product], int]:
        query = session.query(Product).filter(Product.status == 1)
        if category_id:
            query = query.filter(Product.category_id == category_id)
        if keyword:
            query = query.filter(or_(
                Product.name.contains(keyword),
                Product.description.contains(keyword),
            ))
        total = query.count()
        products = query.order_by(Product.sales_count.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return products, total

    @staticmethod
    def list_hot(session: Session, limit: int = 10) -> list[Product]:
        return session.query(Product).filter(Product.status == 1).order_by(
            Product.sales_count.desc()).limit(limit).all()


class CategoryRepo:
    @staticmethod
    def list_all(session: Session) -> list[Category]:
        return session.query(Category).order_by(Category.sort_order).all()

    @staticmethod
    def get_by_id(session: Session, category_id: int) -> Category | None:
        return session.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def create(session: Session, name: str, parent_id: int | None = None) -> Category:
        cat = Category(name=name, parent_id=parent_id)
        session.add(cat)
        session.flush()
        return cat
