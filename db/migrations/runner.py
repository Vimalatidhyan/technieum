"""Root-level SQL-file migration runner.

Scans db/migrations/ for files matching NNN_*.sql in numeric order and
applies any that have not yet been recorded in the schema_migrations table.

Usage:
    from db.migrations.runner import run_migrations
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///./reconx.db")
    run_migrations(engine)

This runner is independent of app/db/migrations/ so both the legacy CLI
and the enterprise API can manage schema evolution from the same SQL source
of truth.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

from sqlalchemy import Engine, text

logger = logging.getLogger(__name__)

_MIGRATIONS_DIR = Path(__file__).parent


def _ensure_migrations_table(engine: Engine) -> None:
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                version     TEXT    NOT NULL UNIQUE,
                applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))


def _applied_versions(engine: Engine) -> set[str]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {r[0] for r in rows}


def run_migrations(engine: Engine) -> None:
    """Apply all pending *.sql migrations found in db/migrations/ in order."""
    _ensure_migrations_table(engine)
    applied = _applied_versions(engine)

    # Collect NNN_*.sql files sorted numerically
    sql_files = sorted(
        _MIGRATIONS_DIR.glob("[0-9][0-9][0-9]_*.sql"),
        key=lambda p: int(re.match(r"^(\d+)", p.stem).group(1)),
    )

    for sql_file in sql_files:
        version = sql_file.stem
        if version in applied:
            logger.debug("Migration %s already applied, skipping.", version)
            continue

        logger.info("Applying migration: %s", version)
        sql_text = sql_file.read_text(encoding="utf-8")

        # Split on semicolons and execute each statement
        statements = [s.strip() for s in sql_text.split(";") if s.strip()]
        with engine.begin() as conn:
            for stmt in statements:
                try:
                    conn.execute(text(stmt))
                except Exception as exc:
                    msg = str(exc).lower()
                    if "already exists" in msg or "duplicate column" in msg:
                        logger.debug("Idempotent DDL, skipping: %.80s", stmt)
                    else:
                        logger.error("Migration %s failed on statement: %.120s", version, stmt)
                        raise
            conn.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:v)"),
                {"v": version},
            )
        logger.info("Migration %s applied successfully.", version)
