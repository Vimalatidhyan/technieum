"""Persistent rate limiting middleware with SQLite storage."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import logging
import sqlite3
import random
from pathlib import Path

logger = logging.getLogger(__name__)
EXEMPT_PATHS = {"/health", "/version", "/docs", "/openapi.json", "/redoc"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_hour: int = 1000):
        super().__init__(app)
        self._limit = requests_per_hour
        self._db_path = self._init_db()

    def _init_db(self) -> str:
        db_dir = Path(__file__).parent.parent.parent.parent / "data"
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "rate_limits.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rate_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_key_ts ON rate_limits(key, timestamp)")
        conn.commit()
        conn.close()
        return db_path

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        key = request.headers.get("X-API-Key", request.client.host if request.client else "unknown")
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)

        conn = None
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()

            if random.randint(1, 10) == 1:
                cursor.execute("DELETE FROM rate_limits WHERE key=? AND timestamp<?",
                               (key, window_start.isoformat()))
                conn.commit()

            cursor.execute("SELECT COUNT(*) FROM rate_limits WHERE key=? AND timestamp>=?",
                           (key, window_start.isoformat()))
            count = cursor.fetchone()[0]

            if count >= self._limit:
                return JSONResponse(
                    {"detail": "Rate limit exceeded", "limit": self._limit, "window": "1 hour"},
                    status_code=429,
                    headers={"Retry-After": "3600"},
                )

            cursor.execute("INSERT INTO rate_limits (key, timestamp) VALUES (?, ?)",
                           (key, now.isoformat()))
            conn.commit()

            response = await call_next(request)
            remaining = max(0, self._limit - count - 1)
            response.headers["X-RateLimit-Limit"] = str(self._limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = (now + timedelta(hours=1)).isoformat()
            return response

        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            return await call_next(request)
        finally:
            if conn:
                conn.close()


rate_limit_middleware = RateLimitMiddleware
