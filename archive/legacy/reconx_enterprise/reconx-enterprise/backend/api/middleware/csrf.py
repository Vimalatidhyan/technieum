"""CSRF protection middleware."""
import secrets
import hashlib
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable


class CSRFMiddleware(BaseHTTPMiddleware):
    """CSRF protection for state-changing operations."""

    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        # API key authenticated routes don't need CSRF protection
        self.exempt_prefixes = ["/api/", "/docs", "/redoc", "/openapi.json"]

    async def dispatch(self, request: Request, call_next: Callable):
        if any(request.url.path.startswith(p) for p in self.exempt_prefixes):
            return await call_next(request)

        if request.method in ["GET", "HEAD", "OPTIONS"]:
            token = self._generate_token()
            response = await call_next(request)
            response.headers["X-CSRF-Token"] = token
            return response

        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            token = request.headers.get("X-CSRF-Token")
            if not token:
                raise HTTPException(status_code=403, detail="CSRF token missing")
            if not self._validate_token(token):
                raise HTTPException(status_code=403, detail="Invalid CSRF token")

        return await call_next(request)

    def _generate_token(self) -> str:
        rand = secrets.token_urlsafe(16)
        h = hashlib.sha256()
        h.update(self.secret_key.encode())
        h.update(rand.encode())
        sig = h.hexdigest()[:16]
        return f"{rand}.{sig}"

    def _validate_token(self, token: str) -> bool:
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return False
            rand, sig = parts
            h = hashlib.sha256()
            h.update(self.secret_key.encode())
            h.update(rand.encode())
            expected = h.hexdigest()[:16]
            return secrets.compare_digest(sig, expected)
        except Exception:
            return False
