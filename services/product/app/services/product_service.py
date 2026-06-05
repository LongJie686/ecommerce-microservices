"""Product business logic - Redis caching with anti-penetration/avalanche."""
from __future__ import annotations

import hashlib

from sqlalchemy.orm import Session

from app.repositories.product_repo import ProductRepo, CategoryRepo
from app.schemas.product import ProductCreate, ProductUpdate
from shared.cache import RedisClient
from shared.response import success, error, paginated


class ProductService:
    def __init__(self, redis: RedisClient, cache_ttl: int = 300):
        self._redis = redis
        self._cache_ttl = cache_ttl

    async def get_product(self, session: Session, product_id: int):
        cache_key = f"product:{product_id}"
        cached = await self._redis.get_with_anti_penetration(cache_key)
        if cached is not None:
            return success(cached)

        product = ProductRepo.get_by_id(session, product_id)
        if not product:
            await self._redis.cache_with_anti_penetration(cache_key, None, expire=self._cache_ttl)
            return error("Product not found", code=404)

        data = {
            "id": product.id, "name": product.name, "price": float(product.price),
            "description": product.description, "image_url": product.image_url,
            "stock": product.stock, "sales_count": product.sales_count, "rating": float(product.rating),
        }
        await self._redis.cache_with_anti_penetration(cache_key, data, expire=self._cache_ttl)
        return success(data)

    def create_product(self, session: Session, data: ProductCreate):
        product = ProductRepo.create(session, **data.model_dump())
        session.flush()
        return success({"id": product.id, "name": product.name})

    async def update_product(self, session: Session, product_id: int, data: ProductUpdate):
        product = ProductRepo.update(session, product_id, **data.model_dump(exclude_none=True))
        if not product:
            return error("Product not found", code=404)
        await self._redis.delete(f"product:{product_id}")
        return success({"id": product.id, "name": product.name})

    async def list_products(self, session: Session, category_id: int | None = None,
                            keyword: str | None = None, page: int = 1, page_size: int = 20):
        keyword_hash = hashlib.sha256((keyword or "").encode()).hexdigest()[:16]
        cache_key = f"products:{category_id}:{keyword_hash}:{page}:{page_size}"
        cached = await self._redis.get_with_anti_penetration(cache_key)
        if cached is not None:
            return cached

        products, total = ProductRepo.list_products(session, category_id, keyword, page, page_size)
        items = [
            {"id": p.id, "name": p.name, "price": float(p.price), "image_url": p.image_url,
             "sales_count": p.sales_count, "rating": float(p.rating)}
            for p in products
        ]
        result = paginated(items, total, page, page_size)
        await self._redis.cache_with_anti_penetration(cache_key, result, expire=self._cache_ttl)
        return result

    async def get_hot_products(self, session: Session, limit: int = 10):
        cache_key = f"products:hot:{limit}"
        cached = await self._redis.get_with_anti_penetration(cache_key)
        if cached is not None:
            return success(cached)

        products = ProductRepo.list_hot(session, limit)
        items = [
            {"id": p.id, "name": p.name, "price": float(p.price), "sales_count": p.sales_count}
            for p in products
        ]
        await self._redis.cache_with_anti_penetration(cache_key, items, expire=60)
        return success(items)


class CategoryService:
    def __init__(self, redis: RedisClient, cache_ttl: int = 600):
        self._redis = redis
        self._cache_ttl = cache_ttl

    async def list_categories(self, session: Session):
        cache_key = "categories:all"
        cached = await self._redis.get_with_anti_penetration(cache_key)
        if cached is not None:
            return success(cached)

        categories = CategoryRepo.list_all(session)
        items = [{"id": c.id, "name": c.name, "parent_id": c.parent_id} for c in categories]
        await self._redis.cache_with_anti_penetration(cache_key, items, expire=self._cache_ttl)
        return success(items)
