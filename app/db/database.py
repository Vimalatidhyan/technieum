"""Database session management.

Single source of truth for:
  - engine creation
  - SessionLocal factory
  - `get_db` FastAPI dependency
  - `apply_migrations()` — runs the versioned migration framework at startup
"""
from __future__ import annotations

import logging
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./reconx.db")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def apply_migrations() -> None:
    """Apply all pending versioned migrations and create missing tables.

    Safe to call on every startup — each migration is idempotent.
    """
    from app.db.base import Base
    from app.db.migrations.versions import register  # noqa: F401 — side-effect: registers migrations
    from app.db.migrations.runner import run_migrations

    # Ensure all tables defined by the ORM exist (creates new tables only,
    # never drops existing ones).
    Base.metadata.create_all(bind=engine)

    # Apply any pending versioned migrations.
    run_migrations(engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: yield a DB session and close it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Database:
    """Convenience wrapper for non-FastAPI contexts (middleware, CLI)."""

    def __init__(self) -> None:
        self.session: Session | None = None

    def connect(self) -> None:
        self.session = SessionLocal()

    def close(self) -> None:
        if self.session:
            self.session.close()
