# Architecture Canonicalization

**Round:** 1 — Canonical Single-Folder Architecture
**Status:** COMPLETE
**Date:** 2026-02-16

---

## Overview

Prior to this round, runtime Python code was spread across three competing
root packages (`backend/`, `api/`, `intelligence/`, `parsers/`), causing
import drift, duplicate implementations, and operational confusion.

All runtime Python code now lives under **`app/`** — the single canonical
root package. Old packages are thin compatibility shims.

---

## Old Path → New Path Mapping

| Old location | New canonical location | Notes |
|---|---|---|
| `backend/db/models.py` | `app/db/models.py` | ORM models |
| `backend/db/database.py` | `app/db/database.py` | Session factory, migrations |
| `backend/db/base.py` | `app/db/base.py` | SQLAlchemy `Base` |
| `backend/api/server.py` | `app/api/server.py` | FastAPI application |
| `backend/api/middleware/auth.py` | `app/api/middleware/auth.py` | Auth middleware |
| `backend/api/middleware/rate_limit.py` | `app/api/middleware/rate_limit.py` | Rate-limit middleware |
| `backend/api/middleware/csrf.py` | `app/api/middleware/csrf.py` | CSRF middleware |
| `backend/api/middleware/logging.py` | `app/api/middleware/logging.py` | Request logging |
| `backend/api/routes/{assets,findings,intel,reports,scans,stream,webhooks}.py` | `app/api/routes/` | API route modules |
| `backend/api/models/{asset,common,finding,intel,scan}.py` | `app/api/models/` | Pydantic schemas |
| `backend/utils/logger.py` | `app/common/logger.py` | Shared logging utility |
| `backend/config.py` | `app/config.py` | Application config |
| `intelligence/**` | `app/intelligence/**` | Intelligence modules |
| `parsers/parser.py` | `app/scanner/parser.py` | Result parsers |

---

## Compatibility Wrapper List

Every `backend/` Python file has been replaced with a one-line re-export
shim (pattern: `from app.X import *`).
Every `api/` route/model file from the old secondary stack is preserved in
`api/` for reference but is no longer the canonical implementation.

| Wrapper file | Points to | Justification |
|---|---|---|
| `backend/db/models.py` | `app.db.models` | Existing test/script imports |
| `backend/db/database.py` | `app.db.database` | Existing test/middleware imports |
| `backend/db/base.py` | `app.db.base` | Alembic + existing imports |
| `backend/api/server.py` | `app.api.server` | Legacy startup scripts |
| `backend/api/middleware/*.py` | `app.api.middleware.*` | Middleware chain |
| `backend/api/routes/*.py` | `app.api.routes.*` | Route modules |
| `backend/api/models/*.py` | `app.api.models.*` | Pydantic schemas |
| `backend/utils/logger.py` | `app.common.logger` | Utility import |
| `api/server.py` (top-level) | `app.api.server` | `uvicorn api.server:app` command |

---

## `app/` Directory Structure

```
app/
├── __init__.py
├── config.py
├── api/
│   ├── server.py          # FastAPI application factory
│   ├── middleware/
│   │   ├── auth.py        # API key auth + in-process cache
│   │   ├── csrf.py        # CSRF with API-key bypass
│   │   ├── logging.py     # Request/response logging
│   │   └── rate_limit.py  # Sliding-window rate limiting (thread-local SQLite)
│   ├── models/            # Pydantic request/response schemas
│   └── routes/            # FastAPI router modules
├── db/
│   ├── base.py            # SQLAlchemy declarative Base
│   ├── database.py        # SessionLocal, get_db, apply_migrations()
│   └── models.py          # 34 ORM models
├── scanner/               # Python interface to shell scanning pipeline
├── intelligence/          # Change-detection, compliance, risk-scoring, threat-intel
├── workers/               # Async worker stubs (Round 4 implementation)
├── web/                   # Web UI helpers
└── common/                # Shared utilities (logger, etc.)
```

---

## Canonical Startup Commands

**Development:**
```bash
# Canonical (recommended)
uvicorn app.api.server:app --reload --host 0.0.0.0 --port 8000

# Backward-compatible (still works)
uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
uvicorn backend.api.server:app --reload --host 0.0.0.0 --port 8000
```

**Production:**
```bash
uvicorn app.api.server:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Round 1 Gate Results

| Gate | Result |
|---|---|
| `python3 -m compileall -q .` | PASS |
| Shell syntax checks (`bash -n`) | PASS |
| `.venv/bin/python -m pytest -q` | PASS (139 passed) |
| `.venv/bin/python -m pytest -q tests` | PASS (30 passed) |
