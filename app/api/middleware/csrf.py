"""CSRF protection middleware.

CSRF protection is skipped when:
  - The request path is on the exempt list.
  - An API key is present (X-API-Key / Authorization: Bearer) — REST API clients
    protected by key-based auth are not vulnerable to CSRF.
  - The HTTP method is safe (GET / HEAD / OPTIONS).
"""
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
        # Paths that never need CSRF (routes mounted under /api/v1/...)
        self.exempt_paths = [
            "/api/v1/webhooks/",
            "/api/v1/stream/",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip for exempt paths
        if any(request.url.path.startswith(p) for p in self.exempt_paths):
            return await call_next(request)

        # Skip for safe methods
        if request.method in ("GET", "HEAD", "OPTIONS"):
            token = self._generate_token()
            response = await call_next(request)
            response.headers["X-CSRF-Token"] = token
            return response

        # Skip for API-key authenticated requests (not subject to CSRF)
        if request.headers.get("X-API-Key") or request.headers.get("Authorization", "").startswith("Bearer "):
            return await call_next(request)

        # Validate CSRF token for browser-originated state-changing requests
        token = request.headers.get("X-CSRF-Token")
        if not token:
            raise HTTPException(
                status_code=403,
                detail="CSRF token missing. Include X-CSRF-Token header.",
            )
        if not self._validate_token(token):
            raise HTTPException(status_code=403, detail="Invalid CSRF token")

        return await call_next(request)

    def _generate_token(self) -> str:
        random_part = secrets.token_urlsafe(16)
        h = hashlib.sha256()
        h.update(self.secret_key.encode())
        h.update(random_part.encode())
        signature = h.hexdigest()[:16]
        return f"{random_part}.{signature}"

    def _validate_token(self, token: str) -> bool:
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return False
            random_part, signature = parts
            h = hashlib.sha256()
            h.update(self.secret_key.encode())
            h.update(random_part.encode())
            expected_sig = h.hexdigest()[:16]
            return secrets.compare_digest(signature, expected_sig)
        except Exception:
            return False
