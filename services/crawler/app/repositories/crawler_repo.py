"""Crawler data access layer."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.crawler import CrawlTask, CrawlResult


class CrawlTaskRepo:
    @staticmethod
    def create(session: Session, platform: str, keyword: str) -> CrawlTask:
        task = CrawlTask(platform=platform, keyword=keyword)
        session.add(task)
        session.flush()
        return task

    @staticmethod
    def get_by_id(session: Session, task_id: int) -> CrawlTask | None:
        return session.query(CrawlTask).filter(CrawlTask.id == task_id).first()

    @staticmethod
    def update_status(session: Session, task_id: int, status: str,
                      total: int = 0, success: int = 0, fail: int = 0,
                      error: str = "") -> None:
        task = session.query(CrawlTask).filter(CrawlTask.id == task_id).first()
        if task:
            task.status = status
            task.total_count = total
            task.success_count = success
            task.fail_count = fail
            if error:
                task.error_message = error
            session.flush()

    @staticmethod
    def list_tasks(session: Session, page: int = 1, page_size: int = 20):
        query = session.query(CrawlTask).order_by(CrawlTask.created_at.desc())
        total = query.count()
        tasks = query.offset((page - 1) * page_size).limit(page_size).all()
        return tasks, total


class CrawlResultRepo:
    @staticmethod
    def bulk_insert(session: Session, results: list[dict]) -> int:
        count = 0
        for data in results:
            result = CrawlResult(**data)
            session.add(result)
            count += 1
        session.flush()
        return count

    @staticmethod
    def get_by_task(session: Session, task_id: int, page: int = 1, page_size: int = 50):
        query = session.query(CrawlResult).filter(CrawlResult.task_id == task_id)
        total = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()
        return results, total
