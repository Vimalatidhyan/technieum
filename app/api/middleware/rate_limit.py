"""Persistent rate limiting middleware with SQLite storage.

Performance improvement: uses a per-thread persistent connection (WAL mode)
instead of opening/closing a new connection on every request.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import logging
import sqlite3
import threading
import random
from pathlib import Path

logger = logging.getLogger(__name__)
EXEMPT_PATHS = {"/health", "/version", "/docs", "/openapi.json", "/redoc"}

# Thread-local storage so each OS thread reuses its own connection.
_local = threading.local()


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_hour: int = 1000):
        super().__init__(app)
        self._limit = requests_per_hour
        self._db_path = self._init_db()

    def _init_db(self) -> str:
        """Create the rate-limit database and schema if needed."""
        db_dir = Path(__file__).parent.parent.parent.parent / "data"
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "rate_limits.db")

        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    key       TEXT    NOT NULL,
                    timestamp TEXT    NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_key_timestamp ON rate_limits(key, timestamp)"
            )
            conn.commit()
        finally:
            conn.close()

        logger.info(f"Rate limit database initialized at {db_path}")
        return db_path

    def _get_conn(self) -> sqlite3.Connection:
        """Return (or lazily create) a per-thread persistent connection."""
        conn = getattr(_local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self._db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            _local.conn = conn
        return conn

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        key = request.headers.get(
            "X-API-Key",
            request.client.host if request.client else "unknown",
        )
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)

        try:
            conn = self._get_conn()

            # Periodic cleanup (~10 % of requests) to keep the table small.
            if random.randint(1, 10) == 1:
                conn.execute(
                    "DELETE FROM rate_limits WHERE key = ? AND timestamp < ?",
                    (key, window_start.isoformat()),
                )
                conn.commit()

            # Check current request count in the sliding window.
            (count,) = conn.execute(
                "SELECT COUNT(*) FROM rate_limits WHERE key = ? AND timestamp >= ?",
                (key, window_start.isoformat()),
            ).fetchone()

            if count >= self._limit:
                return JSONResponse(
                    {"detail": "Rate limit exceeded", "limit": self._limit, "window": "1 hour"},
                    status_code=429,
                    headers={"Retry-After": "3600"},
                )

            # Record this request.
            conn.execute(
                "INSERT INTO rate_limits (key, timestamp) VALUES (?, ?)",
                (key, now.isoformat()),
            )
            conn.commit()

            response = await call_next(request)

            remaining = max(0, self._limit - count - 1)
            response.headers["X-RateLimit-Limit"] = str(self._limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = (now + timedelta(hours=1)).isoformat()
            return response

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Reset the thread-local connection on error so it is recreated next time.
            _local.conn = None
            return await call_next(request)


rate_limit_middleware = RateLimitMiddleware
