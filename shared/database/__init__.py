"""Database connection management with read/write splitting support."""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    """Manages database connections with optional read/write splitting."""

    def __init__(self, write_url: str, read_url: str | None = None, pool_size: int = 10, max_overflow: int = 20):
        self._write_engine = create_engine(
            write_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
        self._read_engine = (
            create_engine(read_url, pool_size=pool_size, max_overflow=max_overflow, pool_pre_ping=True, echo=False)
            if read_url
            else self._write_engine
        )
        self._write_session = sessionmaker(bind=self._write_engine, autocommit=False, autoflush=False)
        self._read_session = sessionmaker(bind=self._read_engine, autocommit=False, autoflush=False)

    def get_write_session(self) -> Generator[Session, None, None]:
        session = self._write_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_read_session(self) -> Generator[Session, None, None]:
        session = self._read_session()
        try:
            yield session
        finally:
            session.close()

    @contextmanager
    def write_session_ctx(self) -> Generator[Session, None, None]:
        """Context manager for use outside of FastAPI Depends (e.g. background tasks)."""
        session = self._write_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def init_tables(self) -> None:
        Base.metadata.create_all(self._write_engine)
        logger.info("Database tables initialized")
