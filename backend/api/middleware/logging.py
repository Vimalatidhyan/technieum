"""Request/response logging middleware."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging, time, uuid

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        req_id = str(uuid.uuid4())[:8]
        start = time.time()
        response = await call_next(request)
        ms = round((time.time() - start) * 1000)
        logger.info(f"[{req_id}] {request.method} {request.url.path} -> {response.status_code} ({ms}ms)")
        return response

logging_middleware = LoggingMiddleware
