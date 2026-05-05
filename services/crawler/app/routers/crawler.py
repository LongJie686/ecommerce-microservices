"""Crawler API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas.crawler import CrawlStartRequest
from app.services.crawler_service import CrawlerService
from shared.cache import RedisClient
from shared.database import DatabaseManager
from shared.mq import KafkaProducer

router = APIRouter()

db = DatabaseManager(write_url=settings.database_url)
redis = RedisClient(url=settings.redis_url)
kafka = KafkaProducer(settings.kafka_bootstrap_servers) if settings.kafka_bootstrap_servers else None

svc = CrawlerService(redis, kafka)


def get_write_session():
    yield from db.get_write_session()


def get_read_session():
    yield from db.get_read_session()


@router.post("/start")
async def start_crawl(req: CrawlStartRequest, bg: BackgroundTasks,
                      session: Session = Depends(get_write_session)):
    result = await svc.start_task(session, req)
    if result.get("code") == 200:
        task_id = result["data"]["task_id"]
        bg.add_task(svc.execute_task, session, task_id)
    return result


@router.get("/tasks")
def list_tasks(page: int = 1, page_size: int = 20,
               session: Session = Depends(get_read_session)):
    return svc.list_tasks(session, page, page_size)


@router.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_read_session)):
    return svc.get_task(session, task_id)


@router.get("/tasks/{task_id}/results")
def get_results(task_id: int, page: int = 1, page_size: int = 50,
                session: Session = Depends(get_read_session)):
    return svc.get_results(session, task_id, page, page_size)
