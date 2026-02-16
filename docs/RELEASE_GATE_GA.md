# Release Gate — GA (General Availability)

All BETA gates must be passed first. Additional GA requirements:

## Performance

- [ ] `scripts/perf_smoke_api.sh` — p95 < 200ms on all endpoints
- [ ] `scripts/perf_scan_queue.sh 20` — completes without error
- [ ] API response times documented in `docs/PERF_BASELINE.md`

## Load Testing

- [ ] Sustained 100 req/s for 5 minutes — no 5xx errors
- [ ] Memory stable over 1-hour soak (no unbounded growth)
- [ ] Auth cache hit rate > 95% under normal load

## Security (enhanced)

- [ ] Penetration test completed (or waived with written justification)
- [ ] OWASP Top 10 reviewed; all applicable items mitigated
- [ ] Rate limiting tested: 1000 req/hour limit enforced per API key
- [ ] CSRF tokens validated end-to-end in browser-based UI

## Observability

- [ ] `GET /api/v1/metrics/` returns current DB counts
- [ ] Structured JSON logs visible in stdout/log aggregation
- [ ] Worker errors logged with `scan_run_id` and `job_id` fields

## Operations

- [ ] `docker compose up -d` starts cleanly from a blank volume
- [ ] `docker compose down && docker compose up -d` (restart) — no data loss
- [ ] Database migration smoke test: start on schema v001, upgrade to latest
- [ ] Rollback procedure tested: `rollback_last()` reverts migration 003 -> 002

## Documentation

- [ ] `docs/RUNBOOK_PRODUCTION.md` reviewed by ops team
- [ ] `docs/PERF_BASELINE.md` measurements taken on production-equivalent hardware
- [ ] Changelog entry written

---

Sign-off: _______________________  Date: ___________
