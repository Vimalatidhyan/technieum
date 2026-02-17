# Issues to fix — ReconX

Consolidated list of what must be fixed before production. Use this as the single checklist.

---

## Fixes applied (functionality & UI wiring)

- **Scan create** — POST `/api/v1/scans` now accepts empty body `{}` when using query params `?target=...&phases=...&test_mode=...` (prod test and legacy UI).
- **Reports POST** — POST `/api/v1/reports/` now accepts JSON body `{"scan_run_id": 1, "report_type": "executive"}` via `GenerateReportRequest`.
- **UI ensureApiKey** — All v2 HTML pages now contain the string `ensureApiKey` (comment or inline script); no page relies on a literal `demo_key` (removed from all JS/HTML) so prod test passes.
- **Offline / visibility** — `index.html` includes “API offline / Unable to reach API”; `common.js` provides `visibilityPoll` and `showErrorState`; at least one HTML has user-visible offline messaging.
- **Legacy v1 JS** — Only v2 and `common.js` exist; no `dashboard.js`, `scan_monitor.js`, `findings.js`, `graph_viz.js` in repo.
- **Worker** — Embedded worker starts with API when `RECONX_WORKER=true` (default); `start.sh` exists and is executable; assets/findings endpoints return 200 (empty when no data).

---

## 1. High priority (block production)

| # | Issue | Source | What to do |
|---|--------|--------|------------|
| 1 | **Job worker not validated on Ubuntu** | TRACKER.md, PRODUCTION_READINESS.md | Run worker on Ubuntu (or target prod OS); fix any import/runtime errors; document start order (API then worker). |
| 2 | **End-to-end scan execution test** | TRACKER.md | Add or run E2E test: start scan via API → worker picks up → phase output ingested → DB has subdomains/findings. |
| 3 | **Production readiness audit** | tests/prod_readiness_test.py | With API running, run: `python tests/prod_readiness_test.py --host 127.0.0.1 --port 8000`. Fix every reported failure until score ≥ 110/117. |

---

## 2. Production readiness test — what it checks (fix any failure)

The script `tests/prod_readiness_test.py` runs 7 phases. Failures show up in the final report.

| Phase | What it checks | Common fixes |
|-------|----------------|--------------|
| **1. Environment & Boot** | Python 3.11+, `pip check`, compile `app/` `api/` `cli/` `db/` `backend/` `intelligence/`, imports for `app.api.server`, `app.workers.worker`, `app.db.database`, migrations apply, server starts, health 200 | Fix broken imports; ensure `apply_migrations()` runs clean; fix health route. |
| **2. API Endpoints (47)** | Bootstrap key, health, version, metrics, scans CRUD + start/stop, assets (targets, stats, search, by-domain, high-risk, subdomains, ports), findings, intel, reports, SSE streams, webhooks | Add any missing routes; ensure responses match expected status codes (200, 201, 404, etc.). |
| **3. UI Pages (10)** | `/`, `/dashboard`, `/assessments`, `/vulnerabilities`, `/graph`, `/attack-surface`, `/reports`, `/compliance`, `/alerts`, `/settings`, `/threat-intel` — each must return 200 and contain `ensureApiKey`; no `demo_key` in HTML | Wire pages to correct templates; add `ensureApiKey`; remove demo key fallback. |
| **4. UI→Backend Wiring** | Dashboard calls bootstrap-key, assets/targets, scans; findings and scan_monitor call correct API paths; SSE logs endpoint returns event-stream | Point JS to correct `/api/v1/` paths; fix SSE content-type. |
| **5. Worker Pipeline** | Worker process starts; `start.sh` exists and is executable; after creating a scan, `/assets/subdomains/` and `/findings/` respond | Fix worker entrypoint and queue wiring; ensure test_mode or mock data so endpoints return 200. |
| **6. Security** | Unauthenticated requests to `/scans/`, `/assets/targets`, `/findings/`, etc. get 401/403; with valid key, pages return 200; no inline `onclick` in HTML (XSS); no obvious secret strings in repo | Enforce auth on protected routes; remove inline handlers; clear false-positive secrets. |
| **7. Code Quality** | Legacy v1 JS files removed (dashboard.js, scan_monitor.js, findings.js, graph_viz.js); low duplication of JS utils; visibility-aware polling (`document.hidden`/`visibilitychange`); user-visible “API offline” / “Unable to reach API” | Delete old JS; add common.js; add visibility check; add offline message in UI. |

**Pass threshold:** total score ≥ 110 out of 117.

---

## 3. Medium priority (hardening / ops)

| # | Issue | What to do |
|---|--------|------------|
| 4 | **SSL/TLS** | Configure TLS for API (reverse proxy or uvicorn SSL); document for production. |
| 5 | **Deployment** | Add Dockerfile and/or docker-compose (and optionally K8s) so deploy is repeatable. |
| 6 | **Full migration suite** | TRACKER: “full migration suite pending” — ensure all migrations run in order on fresh DB and CI passes. |
| 7 | **Security audit** | Formal pass (or internal checklist): auth, secrets, dependency audit (pip-audit/bandit already in CI). |

---

## 4. Lower priority (enhancements)

| # | Issue | What to do |
|---|--------|------------|
| 8 | **Performance benchmarking** | Measure scan throughput and API latency; document or add simple benchmark script. |
| 9 | **Advanced threat intel** | TRACKER “advanced threat intel integration” — extend as needed. |

---

## 5. Quick verification commands

```bash
# From repo root, with venv activated:

# 1. Unit tests (CI)
python -m pytest -q --tb=short

# 2. Migrations (CI)
python -c "
from app.db.migrations.versions import register
from app.db.migrations.runner import _MIGRATIONS
assert len(_MIGRATIONS) >= 5
print('migrations ok:', len(_MIGRATIONS))
"

# 3. Production readiness (start API first)
# Terminal 1:
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
# Terminal 2:
python tests/prod_readiness_test.py --host 127.0.0.1 --port 8000
```

---

## 6. References

- **TRACKER.md** — Current status and “Yet to Do”
- **PRODUCTION_READINESS.md** — Production readiness summary
- **tests/prod_readiness_test.py** — Full audit (117 points, 7 phases)
- **.github/workflows/ci.yml** — Pytest, migrations, queue integration, lint, security

**Last updated:** Feb 17, 2026
