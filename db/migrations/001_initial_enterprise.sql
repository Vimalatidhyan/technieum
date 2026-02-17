-- ReconX Enterprise v2.0 — Initial schema
-- All 25 ORM tables (SQLite-compatible, CREATE TABLE IF NOT EXISTS)
-- This migration is idempotent: safe to run on a database that already
-- has these tables created by SQLAlchemy's create_all().

-- ── Group 1: Core Scanning ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scan_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    domain      TEXT    NOT NULL,
    scan_type   TEXT    DEFAULT 'full',
    status      TEXT    DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    risk_score  INTEGER,
    phase       INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_scan_runs_domain ON scan_runs(domain);
CREATE INDEX IF NOT EXISTS idx_scan_runs_domain_created ON scan_runs(domain, created_at);

CREATE TABLE IF NOT EXISTS subdomains (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id         INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    subdomain           TEXT    NOT NULL,
    ip_address          TEXT,
    is_alive            BOOLEAN DEFAULT 0,
    status_code         INTEGER,
    title               TEXT,
    technologies        TEXT,
    discovered_method   TEXT,
    priority            INTEGER DEFAULT 0,
    first_seen          TIMESTAMP,
    last_seen           TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_subdomains_scan_run ON subdomains(scan_run_id);
CREATE INDEX IF NOT EXISTS idx_subdomains_subdomain ON subdomains(subdomain);

CREATE TABLE IF NOT EXISTS port_scans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE CASCADE,
    port            INTEGER NOT NULL,
    protocol        TEXT    DEFAULT 'tcp',
    state           TEXT,
    service         TEXT,
    version         TEXT,
    banner          TEXT,
    scanned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_port_scans_subdomain ON port_scans(subdomain_id);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE SET NULL,
    vuln_type       TEXT,
    severity        INTEGER DEFAULT 0,
    title           TEXT,
    description     TEXT,
    remediation     TEXT,
    cvss_score      REAL,
    cve_id          TEXT,
    status          TEXT    DEFAULT 'open',
    discovered_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at     TIMESTAMP,
    false_positive  BOOLEAN DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_vulnerabilities_scan_run ON vulnerabilities(scan_run_id);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);

CREATE TABLE IF NOT EXISTS http_headers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE CASCADE,
    header_name     TEXT,
    header_value    TEXT,
    scanned_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Group 2: Intelligence ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS technologies (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    category    TEXT,
    cpe         TEXT
);

CREATE TABLE IF NOT EXISTS domain_technologies (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE CASCADE,
    technology_id   INTEGER REFERENCES technologies(id) ON DELETE CASCADE,
    version         TEXT,
    detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS vulnerability_metadata (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    vuln_id         INTEGER REFERENCES vulnerabilities(id) ON DELETE CASCADE,
    key             TEXT,
    value           TEXT
);

CREATE TABLE IF NOT EXISTS dns_records (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    hostname        TEXT,
    record_type     TEXT,
    value           TEXT,
    ttl             INTEGER,
    resolved_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS isp_locations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    ip_address      TEXT,
    isp             TEXT,
    org             TEXT,
    country         TEXT,
    city            TEXT,
    latitude        REAL,
    longitude       REAL,
    asn             TEXT,
    fetched_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS threat_intel_data (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    indicator_type  TEXT,
    indicator_value TEXT,
    severity        INTEGER,
    source          TEXT,
    raw_data        TEXT,
    last_updated    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(indicator_type, indicator_value, source)
);

-- ── Group 3: Compliance & Reporting ──────────────────────────────────────

CREATE TABLE IF NOT EXISTS compliance_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    framework       TEXT,
    score           REAL,
    summary         TEXT,
    generated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS compliance_findings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    compliance_report_id INTEGER REFERENCES compliance_reports(id) ON DELETE CASCADE,
    control_id          TEXT,
    control_name        TEXT,
    status              TEXT,
    evidence            TEXT
);

CREATE TABLE IF NOT EXISTS risk_scores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE SET NULL,
    score           REAL,
    factors         TEXT,
    calculated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type  TEXT,
    user_id     TEXT,
    resource    TEXT,
    details     TEXT,
    ip_address  TEXT,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS asset_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    snapshot_data   TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_asset_snapshots_scan_run ON asset_snapshots(scan_run_id);

-- ── Group 4: Change Tracking ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS asset_changes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    asset_type      TEXT,
    asset_id        INTEGER,
    change_type     TEXT,
    before_value    TEXT,
    after_value     TEXT,
    detected_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS change_notifications (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_change_id INTEGER REFERENCES asset_changes(id) ON DELETE CASCADE,
    channel         TEXT,
    recipient       TEXT,
    sent_at         TIMESTAMP,
    status          TEXT    DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS website_snapshots (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    subdomain_id    INTEGER REFERENCES subdomains(id) ON DELETE CASCADE,
    content_hash    TEXT,
    screenshot_path TEXT,
    captured_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ── Group 5: Integration & System ────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scanner_integrations (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL UNIQUE,
    integration_type TEXT,
    config          TEXT,
    is_active       BOOLEAN DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scan_runner_metadata (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    worker_id       TEXT,
    hostname        TEXT,
    pid             INTEGER,
    started_at      TIMESTAMP,
    finished_at     TIMESTAMP,
    exit_code       INTEGER
);

CREATE TABLE IF NOT EXISTS api_keys (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    key_hash        TEXT    NOT NULL UNIQUE,
    name            TEXT,
    user_identifier TEXT,
    is_active       BOOLEAN DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at      TIMESTAMP,
    last_used       TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash);

CREATE TABLE IF NOT EXISTS saved_reports (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    title           TEXT,
    format          TEXT    DEFAULT 'pdf',
    file_path       TEXT,
    generated_by    TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS scheduled_scans (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    domain          TEXT    NOT NULL,
    scan_type       TEXT    DEFAULT 'full',
    cron_expression TEXT,
    is_active       BOOLEAN DEFAULT 1,
    last_run_at     TIMESTAMP,
    next_run_at     TIMESTAMP,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS known_vulnerabilities (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id      TEXT    NOT NULL UNIQUE,
    title       TEXT,
    description TEXT,
    cvss_score  REAL,
    severity    TEXT,
    published   TIMESTAMP,
    modified    TIMESTAMP,
    references  TEXT
);

-- ── Worker / Streaming tables ─────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scan_jobs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    status          TEXT    DEFAULT 'queued',
    worker_id       TEXT,
    queued_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at      TIMESTAMP,
    finished_at     TIMESTAMP,
    error           TEXT
);

CREATE INDEX IF NOT EXISTS idx_scan_jobs_status ON scan_jobs(status);

CREATE TABLE IF NOT EXISTS scan_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id     INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE,
    event_type      TEXT,
    level           TEXT    DEFAULT 'info',
    message         TEXT,
    data            TEXT,
    phase           INTEGER,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_scan_events_scan_run ON scan_events(scan_run_id);
CREATE INDEX IF NOT EXISTS idx_scan_events_created ON scan_events(created_at);

CREATE TABLE IF NOT EXISTS scan_progress (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_run_id         INTEGER REFERENCES scan_runs(id) ON DELETE CASCADE UNIQUE,
    status              TEXT    DEFAULT 'pending',
    current_phase       INTEGER DEFAULT 0,
    progress_percentage INTEGER DEFAULT 0,
    subdomains_found    INTEGER DEFAULT 0,
    ports_found         INTEGER DEFAULT 0,
    vulnerabilities_found INTEGER DEFAULT 0,
    last_update         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS webhook_configs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT,
    url             TEXT    NOT NULL,
    secret          TEXT,
    events          TEXT,
    is_active       BOOLEAN DEFAULT 1,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_triggered  TIMESTAMP
);
