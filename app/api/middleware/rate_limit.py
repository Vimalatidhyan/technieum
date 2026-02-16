"""Persistent rate limiting middleware with SQLite storage.

Security improvements over previous version:
  - API keys are hashed (SHA-256) before storage — no raw secrets at rest.
  - Cleanup runs deterministically when the per-key row count exceeds a threshold
    instead of randomly, bounding table growth without per-request overhead.
  - Connection is reused per-thread (WAL mode) to minimise DB overhead.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime, timedelta, timezone
import hashlib
import logging
import sqlite3
import threading
from pathlib import Path

logger = logging.getLogger(__name__)
EXEMPT_PATHS = {"/health", "/api/health", "/version", "/docs", "/openapi.json", "/redoc"}

# Per-key cleanup threshold: when a key has accumulated this many old rows,
# delete them.  This bounds table growth without running on every request.
_CLEANUP_THRESHOLD = 200

# Thread-local so each OS thread reuses its own connection.
_local = threading.local()


def _hash_key(raw_key: str) -> str:
    """One-way hash of an API key or IP for storage (no raw secrets at rest)."""
    return hashlib.sha256(raw_key.encode()).hexdigest()[:32]


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_hour: int = 1000):
        super().__init__(app)
        self._limit = requests_per_hour
        self._db_path = self._init_db()

    def _init_db(self) -> str:
        """Create (or migrate) the rate-limit database and schema."""
        db_dir = Path(__file__).parent.parent.parent.parent / "data"
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "rate_limits.db")

        conn = sqlite3.connect(db_path)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            # Check whether table exists with old schema (column 'key')
            cols = {
                row[1]
                for row in conn.execute(
                    "PRAGMA table_info(rate_limits)"
                ).fetchall()
            }
            if cols and "key" in cols and "key_hash" not in cols:
                # Migrate: drop old table (rate-limit data is ephemeral, no user data)
                conn.execute("DROP TABLE rate_limits")
                conn.execute("DROP INDEX IF EXISTS idx_key_timestamp")
                logger.info("Rate limit DB schema migrated (key→key_hash)")

            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    id         INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash   TEXT    NOT NULL,
                    timestamp  TEXT    NOT NULL
                )
            """)
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_kh_ts ON rate_limits(key_hash, timestamp)"
            )
            conn.commit()
        finally:
            conn.close()

        logger.info("Rate limit database initialized at %s", db_path)
        return db_path

    def _get_conn(self) -> sqlite3.Connection:
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

        raw_key = request.headers.get(
            "X-API-Key",
            request.client.host if request.client else "unknown",
        )
        key_hash = _hash_key(raw_key)
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(hours=1)

        try:
            conn = self._get_conn()

            (count,) = conn.execute(
                "SELECT COUNT(*) FROM rate_limits WHERE key_hash=? AND timestamp>=?",
                (key_hash, window_start.isoformat()),
            ).fetchone()

            if count >= self._limit:
                return JSONResponse(
                    {"detail": "Rate limit exceeded", "limit": self._limit, "window": "1 hour"},
                    status_code=429,
                    headers={"Retry-After": "3600"},
                )

            conn.execute(
                "INSERT INTO rate_limits (key_hash, timestamp) VALUES (?, ?)",
                (key_hash, now.isoformat()),
            )

            # Bounded cleanup: only when old rows accumulate beyond threshold.
            if count > _CLEANUP_THRESHOLD:
                conn.execute(
                    "DELETE FROM rate_limits WHERE key_hash=? AND timestamp<?",
                    (key_hash, window_start.isoformat()),
                )

            conn.commit()

            response = await call_next(request)
            remaining = max(0, self._limit - count - 1)
            response.headers["X-RateLimit-Limit"] = str(self._limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = (now + timedelta(hours=1)).isoformat()
            return response

        except Exception as e:
            logger.error("Rate limiting error: %s", e)
            _local.conn = None  # Reset on error so next request gets fresh connection
            return await call_next(request)


rate_limit_middleware = RateLimitMiddleware
