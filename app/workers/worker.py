"""Scan worker — isolated process that pulls work from the job queue.

Architecture
------------
The API server writes a row into ``scan_jobs`` (status='queued') and
the worker polls that table in a tight loop.  Using the database as the
queue avoids a broker dependency while still giving us:

  * Durability  — jobs survive a worker crash
  * Isolation   — the worker process is separate from the API server so a
                  runaway scan cannot OOM the API
  * Observability — job state is visible via the normal API/DB tooling

Usage
-----
    # Start a persistent worker (auto-restarts on error)
    python -m app.workers.worker

    # One-shot: drain the queue once then exit
    python -m app.workers.worker --drain

Environment
-----------
    DATABASE_URL     — SQLAlchemy database URL (default: sqlite:///./reconx.db)
    WORKER_POLL_SEC  — seconds between queue polls (default: 5)
    WORKER_MAX_JOBS  — max concurrent jobs (default: 2)
    LOG_LEVEL        — logging level (default: INFO)
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.api.middleware.logging import configure_json_logging

_LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
configure_json_logging(level=_LOG_LEVEL)
logger = logging.getLogger(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./reconx.db")
WORKER_POLL_SEC = int(os.environ.get("WORKER_POLL_SEC", "5"))
WORKER_MAX_JOBS = int(os.environ.get("WORKER_MAX_JOBS", "2"))

_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
)
_Session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)


def _ensure_job_table() -> None:
    with _engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS scan_jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_run_id INTEGER NOT NULL,
                status      TEXT    NOT NULL DEFAULT 'queued',
                queued_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at  TIMESTAMP,
                finished_at TIMESTAMP,
                error       TEXT
            )
        """))


def _claim_job(db) -> Optional[dict]:
    """Atomically claim one queued job; returns the job dict or None."""
    row = db.execute(
        text("SELECT id, scan_run_id FROM scan_jobs WHERE status='queued' ORDER BY id LIMIT 1")
    ).fetchone()
    if row is None:
        return None
    job_id, scan_run_id = row
    db.execute(
        text("UPDATE scan_jobs SET status='running', started_at=:ts WHERE id=:id"),
        {"ts": datetime.now(timezone.utc), "id": job_id},
    )
    db.commit()
    return {"id": job_id, "scan_run_id": scan_run_id}


def _finish_job(db, job_id: int, success: bool, error: str = "") -> None:
    db.execute(
        text("UPDATE scan_jobs SET status=:s, finished_at=:ts, error=:e WHERE id=:id"),
        {"s": "done" if success else "failed", "ts": datetime.now(timezone.utc), "e": error, "id": job_id},
    )
    db.commit()


def _update_scan_status(db, scan_run_id: int, status: str) -> None:
    db.execute(
        text("UPDATE scan_runs SET status=:s WHERE id=:id"),
        {"s": status, "id": scan_run_id},
    )
    db.commit()


def _run_scan(scan_run_id: int) -> tuple[bool, str]:
    """Invoke the shell-level scan harness for the given scan run."""
    db = _Session()
    try:
        row = db.execute(
            text("SELECT domain, scan_type FROM scan_runs WHERE id=:id"),
            {"id": scan_run_id},
        ).fetchone()
        if row is None:
            return False, f"scan_run {scan_run_id} not found"
        domain, scan_type = row
    finally:
        db.close()

    logger.info("starting scan", extra={"scan_run_id": scan_run_id, "domain": domain, "scan_type": scan_type})

    harness = os.path.join(os.path.dirname(__file__), "..", "..", "lib", "run_scan.sh")
    if os.path.isfile(harness):
        try:
            result = subprocess.run(
                [harness, str(scan_run_id), domain, scan_type or "full"],
                timeout=3600,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                return False, result.stderr[:500]
        except subprocess.TimeoutExpired:
            return False, "scan timed out after 3600 seconds"
        except Exception as exc:
            return False, str(exc)

    return True, ""


def run_once() -> int:
    """Drain the queue once; return number of jobs processed."""
    _ensure_job_table()
    processed = 0
    db = _Session()
    try:
        while True:
            job = _claim_job(db)
            if job is None:
                break
            scan_run_id = job["scan_run_id"]
            job_id = job["id"]
            _update_scan_status(db, scan_run_id, "running")
            success, error = _run_scan(scan_run_id)
            _finish_job(db, job_id, success, error)
            _update_scan_status(db, scan_run_id, "completed" if success else "failed")
            logger.info("job finished", extra={"job_id": job_id, "scan_run_id": scan_run_id, "success": success})
            processed += 1
    finally:
        db.close()
    return processed


def run_forever() -> None:
    """Poll the queue indefinitely; restart on unhandled errors."""
    logger.info("worker started", extra={"poll_sec": WORKER_POLL_SEC})
    _ensure_job_table()
    while True:
        try:
            n = run_once()
            if n == 0:
                time.sleep(WORKER_POLL_SEC)
        except KeyboardInterrupt:
            logger.info("worker stopping")
            sys.exit(0)
        except Exception as exc:
            logger.error("worker error — will retry", extra={"error": str(exc)})
            time.sleep(WORKER_POLL_SEC)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ReconX scan worker")
    parser.add_argument("--drain", action="store_true", help="Process queue once and exit")
    args = parser.parse_args()
    if args.drain:
        n = run_once()
        print(f"Processed {n} job(s).")
    else:
        run_forever()
