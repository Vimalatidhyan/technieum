"""FastAPI server for ReconX Enterprise v2.0."""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.auth import AuthMiddleware
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.logging import LoggingMiddleware, configure_json_logging
from app.api.middleware.csrf import CSRFMiddleware
from app.db.database import Database, apply_migrations

_LOG_LEVEL = getattr(logging, os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
configure_json_logging(level=_LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown."""
    logger.info("ReconX Enterprise API v2.0 starting...")
    apply_migrations()
    db = Database()
    db.connect()
    app.state.db = db
    yield
    logger.info("ReconX Enterprise API shutting down...")
    db.close()


app = FastAPI(
    title="ReconX Enterprise API",
    description="Attack Surface Management Platform v2.0",
    version="2.0.0",
    lifespan=lifespan,
)

# Middleware (order matters — outermost first)
# CORS: Specific origins in production, localhost for dev (don't use wildcard with credentials)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, requests_per_hour=1000)
app.add_middleware(CSRFMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Import and register routers
from app.api.routes import scans, assets, findings, intel, reports, stream, webhooks
from app.api.routes import metrics as metrics_router

app.include_router(scans.router, prefix="/api/v1/scans", tags=["scans"])
app.include_router(assets.router, prefix="/api/v1/assets", tags=["assets"])
app.include_router(findings.router, prefix="/api/v1/findings", tags=["findings"])
app.include_router(intel.router, prefix="/api/v1/intel", tags=["threat-intel"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(stream.router, prefix="/api/v1/stream", tags=["streaming"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(metrics_router.router, prefix="/api/v1/metrics", tags=["observability"])


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/version", tags=["system"])
async def version():
    """Version endpoint."""
    return {"version": "2.0.0", "name": "ReconX Enterprise"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
