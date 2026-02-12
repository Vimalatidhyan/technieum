"""Simple in-memory rate limiting middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from collections import defaultdict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
EXEMPT_PATHS = {"/health", "/version", "/docs", "/openapi.json", "/redoc"}

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_hour: int = 1000):
        super().__init__(app)
        self._counts: dict = defaultdict(list)
        self._limit = requests_per_hour

    async def dispatch(self, request: Request, call_next):
        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)
        key = request.headers.get("X-API-Key", request.client.host if request.client else "unknown")
        now = datetime.utcnow()
        window_start = now - timedelta(hours=1)
        self._counts[key] = [t for t in self._counts[key] if t > window_start]
        if len(self._counts[key]) >= self._limit:
            return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429, headers={"Retry-After": "3600"})
        self._counts[key].append(now)
        response = await call_next(request)
        remaining = max(0, self._limit - len(self._counts[key]))
        response.headers["X-RateLimit-Limit"] = str(self._limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

rate_limit_middleware = RateLimitMiddleware
