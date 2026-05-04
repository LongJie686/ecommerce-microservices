"""Crawler business logic - async crawling simulation + Kafka integration."""
from __future__ import annotations

import json
import random
import asyncio
from datetime import datetime

from sqlalchemy.orm import Session

from app.repositories.crawler_repo import CrawlTaskRepo, CrawlResultRepo
from app.schemas.crawler import CrawlStartRequest
from shared.cache import RedisClient
from shared.mq import KafkaProducer
from shared.response import success, error, paginated


class CrawlerService:
    def __init__(self, redis: RedisClient, kafka_producer: KafkaProducer | None = None):
        self._redis = redis
        self._kafka = kafka_producer

    def start_task(self, session: Session, req: CrawlStartRequest):
        dedupe_key = f"crawl:lock:{req.platform}:{req.keyword}"
        lock = asyncio.get_event_loop().run_until_complete(
            self._redis.acquire_lock(dedupe_key, timeout=300)
        )
        if not lock:
            return error("A crawl task for this keyword is already running", code=409)

        task = CrawlTaskRepo.create(session, req.platform, req.keyword)
        session.flush()
        return success({"task_id": task.id, "status": task.status})

    async def execute_task(self, session: Session, task_id: int):
        task = CrawlTaskRepo.get_by_id(session, task_id)
        if not task:
            return

        CrawlTaskRepo.update_status(session, task_id, "running")
        try:
            results = await self._simulate_crawl(task.platform, task.keyword, task_id)

            count = CrawlResultRepo.bulk_insert(session, results)
            CrawlTaskRepo.update_status(
                session, task_id, "completed",
                total=len(results), success=count, fail=len(results) - count,
            )

            if self._kafka:
                for item in results:
                    await self._kafka.send("crawler-results", {
                        "task_id": task_id,
                        "platform": task.platform,
                        "product_name": item.get("product_name", ""),
                        "price": item.get("price", 0),
                        "sales_count": item.get("sales_count", 0),
                    })
        except Exception as e:
            CrawlTaskRepo.update_status(session, task_id, "failed", error=str(e))

    async def _simulate_crawl(self, platform: str, keyword: str, task_id: int) -> list[dict]:
        """Simulated crawl - in real project this would use httpx/aiohttp."""
        await asyncio.sleep(0.1)
        items = []
        for i in range(random.randint(5, 20)):
            items.append({
                "task_id": task_id,
                "platform": platform,
                "product_name": f"{keyword} - {platform} product {i+1}",
                "price": round(random.uniform(50, 5000), 2),
                "original_price": round(random.uniform(100, 6000), 2),
                "sales_count": random.randint(100, 50000),
                "rating": round(random.uniform(3.5, 5.0), 1),
                "shop_name": f"{platform}_shop_{random.randint(1, 100)}",
                "product_url": f"https://{platform}.com/item/{random.randint(10000, 99999)}",
                "category": keyword,
            })
        return items

    def get_task(self, session: Session, task_id: int):
        task = CrawlTaskRepo.get_by_id(session, task_id)
        if not task:
            return error("Task not found", code=404)
        return success({
            "id": task.id, "platform": task.platform, "keyword": task.keyword,
            "status": task.status, "total_count": task.total_count,
            "success_count": task.success_count, "created_at": str(task.created_at),
        })

    def get_results(self, session: Session, task_id: int, page: int = 1, page_size: int = 50):
        results, total = CrawlResultRepo.get_by_task(session, task_id, page, page_size)
        items = [
            {"id": r.id, "product_name": r.product_name, "price": r.price,
             "sales_count": r.sales_count, "shop_name": r.shop_name}
            for r in results
        ]
        return paginated(items, total, page, page_size)

    def list_tasks(self, session: Session, page: int = 1, page_size: int = 20):
        tasks, total = CrawlTaskRepo.list_tasks(session, page, page_size)
        items = [
            {"id": t.id, "platform": t.platform, "keyword": t.keyword,
             "status": t.status, "total_count": t.total_count}
            for t in tasks
        ]
        return paginated(items, total, page, page_size)
