"""Crawler API routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.dependencies import db, redis, kafka
from app.schemas.crawler import CrawlStartRequest
from app.services.crawler_service import CrawlerService

router = APIRouter()
svc = CrawlerService(db, redis, kafka)


def get_write_session():
    yield from db.get_write_session()


def get_read_session():
    yield from db.get_read_session()


@router.post("/start")
async def start_crawl(req: CrawlStartRequest, bg: BackgroundTasks,
                      session: Session = Depends(get_write_session)):
    result, lock_id, dedupe_key = await svc.start_task(session, req)
    if result.get("code") == 200 and lock_id:
        task_id = result["data"]["task_id"]
        bg.add_task(svc.execute_task, task_id, lock_id, dedupe_key)
    return result


@router.get("/tasks")
def list_tasks(page: int = 1, page_size: int = Query(default=20, ge=1, le=100),
               session: Session = Depends(get_read_session)):
    return svc.list_tasks(session, page, page_size)


@router.get("/tasks/{task_id}")
def get_task(task_id: int, session: Session = Depends(get_read_session)):
    return svc.get_task(session, task_id)


@router.get("/tasks/{task_id}/results")
def get_results(task_id: int, page: int = 1, page_size: int = Query(default=50, ge=1, le=200),
                session: Session = Depends(get_read_session)):
    return svc.get_results(session, task_id, page, page_size)
