#!/usr/bin/env python3
"""
ReconX Database Manager
SQLite3 with WAL Mode for concurrent access
"""

import sqlite3
import threading
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class DatabaseManager:
    """Database Manager with WAL mode enabled"""

    def __init__(self, db_path: str = "reconx.db"):
        self.db_path = db_path
        self.local = threading.local()
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get thread-local database connection"""
        if not hasattr(self.local, 'connection') or self.local.connection is None:
            self.local.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                timeout=30.0
            )
            self.local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for concurrent reads/writes
            self.local.connection.execute("PRAGMA journal_mode=WAL")
            self.local.connection.execute("PRAGMA synchronous=NORMAL")
            self.local.connection.execute("PRAGMA cache_size=10000")
            self.local.connection.execute("PRAGMA temp_store=MEMORY")
        return self.local.connection

    def _init_database(self):
        """Initialize database schema"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Scan Progress Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scan_progress (
                target TEXT PRIMARY KEY,
                phase1_done BOOLEAN DEFAULT 0,
                phase2_done BOOLEAN DEFAULT 0,
                phase3_done BOOLEAN DEFAULT 0,
                phase4_done BOOLEAN DEFAULT 0,
                phase1_partial BOOLEAN DEFAULT 0,
                phase2_partial BOOLEAN DEFAULT 0,
                phase3_partial BOOLEAN DEFAULT 0,
                phase4_partial BOOLEAN DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tool Runs Table (for per-tool status tracking)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                phase INTEGER,
                tool_name TEXT,
                command TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                exit_code INTEGER,
                status TEXT,
                output_file TEXT,
                error_file TEXT,
                duration_seconds REAL,
                records_found INTEGER DEFAULT 0
            )
        """)

        # Acquisitions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS acquisitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                company TEXT,
                domain TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target, company, domain)
            )
        """)

        # Subdomains Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS subdomains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                host TEXT,
                ip TEXT,
                is_alive BOOLEAN DEFAULT 0,
                status_code INTEGER,
                source_tools TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target, host)
            )
        """)

        # Ports Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                host TEXT,
                port INTEGER,
                protocol TEXT,
                service TEXT,
                version TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target, host, port)
            )
        """)

        # URLs Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                url TEXT,
                source_tool TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target, url, source_tool)
            )
        """)

        # Leaks Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                leak_type TEXT,
                url TEXT,
                info TEXT,
                severity TEXT DEFAULT 'info',
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Vulnerabilities Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                host TEXT,
                tool TEXT,
                severity TEXT,
                name TEXT,
                info TEXT,
                cve TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Infrastructure Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS infrastructure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                host TEXT,
                ip TEXT,
                asn TEXT,
                org TEXT,
                cloud_provider TEXT,
                cdn TEXT,
                technologies TEXT,
                discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(target, host)
            )
        """)

        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subdomains_target ON subdomains(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_subdomains_alive ON subdomains(is_alive)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_urls_target ON urls(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vulns_target ON vulnerabilities(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vulns_severity ON vulnerabilities(severity)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_ports_target ON ports(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leaks_target ON leaks(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_runs_target ON tool_runs(target)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_runs_phase ON tool_runs(phase)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tool_runs_status ON tool_runs(status)")

        conn.commit()

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return cursor"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor

    def executemany(self, query: str, params_list: List[tuple]) -> None:
        """Execute many queries in a single transaction"""
        if not params_list:
            return
        conn = self._get_connection()
        conn.execute("BEGIN")
        try:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def fetchone(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Execute query and fetch one result"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def fetchall(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Execute query and fetch all results"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    # ==================== SCAN PROGRESS ====================

    def init_target(self, target: str) -> None:
        """Initialize target in scan_progress"""
        self.execute(
            "INSERT OR IGNORE INTO scan_progress (target) VALUES (?)",
            (target,)
        )

    def update_phase(self, target: str, phase: int, done: bool = True, partial: bool = False) -> None:
        """Update phase completion status"""
        phase_col = f"phase{phase}_done"
        partial_col = f"phase{phase}_partial"
        self.execute(
            f"UPDATE scan_progress SET {phase_col} = ?, {partial_col} = ?, updated_at = CURRENT_TIMESTAMP WHERE target = ?",
            (int(done), int(partial), target)
        )

    def get_progress(self, target: str) -> Optional[Dict[str, Any]]:
        """Get scan progress for target"""
        row = self.fetchone(
            "SELECT * FROM scan_progress WHERE target = ?",
            (target,)
        )
        return dict(row) if row else None

    # ==================== TOOL RUNS ====================

    def start_tool_run(self, target: str, phase: int, tool_name: str, command: str = None) -> int:
        """Record tool execution start"""
        cursor = self.execute("""
            INSERT INTO tool_runs (target, phase, tool_name, command, status)
            VALUES (?, ?, ?, ?, 'running')
        """, (target, phase, tool_name, command or ''))
        return cursor.lastrowid

    def complete_tool_run(self, run_id: int, exit_code: int, output_file: str = None,
                         error_file: str = None, records_found: int = 0) -> None:
        """Mark tool execution as complete"""
        status = 'success' if exit_code == 0 else 'failed'
        self.execute("""
            UPDATE tool_runs SET
                completed_at = CURRENT_TIMESTAMP,
                exit_code = ?,
                status = ?,
                output_file = ?,
                error_file = ?,
                records_found = ?,
                duration_seconds = (julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 86400
            WHERE id = ?
        """, (exit_code, status, output_file, error_file, records_found, run_id))

    def get_tool_runs(self, target: str, phase: int = None) -> List[Dict[str, Any]]:
        """Get tool runs for target"""
        if phase:
            rows = self.fetchall(
                "SELECT * FROM tool_runs WHERE target = ? AND phase = ? ORDER BY started_at",
                (target, phase)
            )
        else:
            rows = self.fetchall(
                "SELECT * FROM tool_runs WHERE target = ? ORDER BY started_at",
                (target,)
            )
        return [dict(row) for row in rows]

    def get_failed_tools(self, target: str, phase: int = None) -> List[str]:
        """Get list of failed tool names"""
        if phase:
            rows = self.fetchall(
                "SELECT tool_name FROM tool_runs WHERE target = ? AND phase = ? AND status = 'failed'",
                (target, phase)
            )
        else:
            rows = self.fetchall(
                "SELECT tool_name FROM tool_runs WHERE target = ? AND status = 'failed'",
                (target,)
            )
        return [row['tool_name'] for row in rows]

    def get_successful_tools(self, target: str, phase: int = None) -> List[str]:
        """Get list of successful tool names"""
        if phase:
            rows = self.fetchall(
                "SELECT tool_name FROM tool_runs WHERE target = ? AND phase = ? AND status = 'success'",
                (target, phase)
            )
        else:
            rows = self.fetchall(
                "SELECT tool_name FROM tool_runs WHERE target = ? AND status = 'success'",
                (target,)
            )
        return [row['tool_name'] for row in rows]

    # ==================== ACQUISITIONS ====================

    def insert_acquisition(self, target: str, company: str, domain: str) -> None:
        """Insert acquisition data"""
        self.execute(
            "INSERT OR IGNORE INTO acquisitions (target, company, domain) VALUES (?, ?, ?)",
            (target, company, domain)
        )

    def insert_acquisitions_bulk(self, target: str, acquisitions: List[Dict[str, str]]) -> None:
        """Bulk insert acquisitions"""
        data = [(target, acq.get('company', ''), acq.get('domain', '')) for acq in acquisitions]
        self.executemany(
            "INSERT OR IGNORE INTO acquisitions (target, company, domain) VALUES (?, ?, ?)",
            data
        )

    # ==================== SUBDOMAINS ====================

    def insert_subdomain(self, target: str, host: str, ip: str = None,
                        is_alive: bool = False, status_code: int = None,
                        source_tool: str = None) -> None:
        """Insert or update subdomain"""
        self.execute("""
            INSERT INTO subdomains (target, host, ip, is_alive, status_code, source_tools)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(target, host) DO UPDATE SET
                ip = COALESCE(excluded.ip, ip),
                is_alive = excluded.is_alive OR is_alive,
                status_code = COALESCE(excluded.status_code, status_code),
                source_tools = CASE
                    WHEN source_tools IS NULL THEN excluded.source_tools
                    WHEN excluded.source_tools IS NULL THEN source_tools
                    WHEN source_tools LIKE '%' || excluded.source_tools || '%' THEN source_tools
                    ELSE source_tools || ',' || excluded.source_tools
                END
        """, (target, host, ip, int(is_alive), status_code, source_tool))

    def insert_subdomains_bulk(self, target: str, subdomains: List[Dict[str, Any]]) -> None:
        """Bulk insert/update subdomains using ON CONFLICT DO UPDATE to preserve data"""
        conn = self._get_connection()
        conn.execute("BEGIN")
        try:
            for sub in subdomains:
                conn.execute("""
                    INSERT INTO subdomains (target, host, ip, is_alive, status_code, source_tools)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(target, host) DO UPDATE SET
                        ip = COALESCE(excluded.ip, ip),
                        is_alive = excluded.is_alive OR is_alive,
                        status_code = COALESCE(excluded.status_code, status_code),
                        source_tools = CASE
                            WHEN source_tools IS NULL THEN excluded.source_tools
                            WHEN excluded.source_tools IS NULL THEN source_tools
                            WHEN source_tools LIKE '%' || excluded.source_tools || '%' THEN source_tools
                            ELSE source_tools || ',' || excluded.source_tools
                        END
                """, (target, sub['host'], sub.get('ip'), int(sub.get('is_alive', False)),
                      sub.get('status_code'), sub.get('source_tool')))
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def get_alive_hosts(self, target: str) -> List[str]:
        """Get all alive hosts for target"""
        rows = self.fetchall(
            "SELECT host FROM subdomains WHERE target = ? AND is_alive = 1",
            (target,)
        )
        return [row['host'] for row in rows]

    def get_all_subdomains(self, target: str) -> List[str]:
        """Get all subdomains for target"""
        rows = self.fetchall(
            "SELECT host FROM subdomains WHERE target = ?",
            (target,)
        )
        return [row['host'] for row in rows]

    # ==================== PORTS ====================

    def insert_port(self, target: str, host: str, port: int,
                   protocol: str = 'tcp', service: str = None, version: str = None) -> None:
        """Insert port data"""
        self.execute("""
            INSERT OR IGNORE INTO ports (target, host, port, protocol, service, version)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (target, host, port, protocol, service, version))

    def insert_ports_bulk(self, target: str, ports: List[Dict[str, Any]]) -> None:
        """Bulk insert ports"""
        data = [
            (target, p['host'], p['port'], p.get('protocol', 'tcp'),
             p.get('service'), p.get('version'))
            for p in ports
        ]
        self.executemany("""
            INSERT OR IGNORE INTO ports (target, host, port, protocol, service, version)
            VALUES (?, ?, ?, ?, ?, ?)
        """, data)

    # ==================== URLS ====================

    def insert_url(self, target: str, url: str, source_tool: str) -> None:
        """Insert URL"""
        self.execute(
            "INSERT OR IGNORE INTO urls (target, url, source_tool) VALUES (?, ?, ?)",
            (target, url, source_tool)
        )

    def insert_urls_bulk(self, target: str, urls: List[Dict[str, str]]) -> None:
        """Bulk insert URLs"""
        data = [(target, url['url'], url.get('source_tool', 'unknown')) for url in urls]
        self.executemany(
            "INSERT OR IGNORE INTO urls (target, url, source_tool) VALUES (?, ?, ?)",
            data
        )

    # ==================== LEAKS ====================

    def insert_leak(self, target: str, leak_type: str, url: str,
                   info: str, severity: str = 'info') -> None:
        """Insert leak data"""
        self.execute("""
            INSERT INTO leaks (target, leak_type, url, info, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (target, leak_type, url, info, severity))

    def insert_leaks_bulk(self, target: str, leaks: List[Dict[str, str]]) -> None:
        """Bulk insert leaks"""
        data = [
            (target, leak['leak_type'], leak['url'], leak.get('info', ''),
             leak.get('severity', 'info'))
            for leak in leaks
        ]
        self.executemany("""
            INSERT INTO leaks (target, leak_type, url, info, severity)
            VALUES (?, ?, ?, ?, ?)
        """, data)

    # ==================== VULNERABILITIES ====================

    def insert_vulnerability(self, target: str, host: str, tool: str,
                           severity: str, name: str, info: str, cve: str = None) -> None:
        """Insert vulnerability"""
        self.execute("""
            INSERT INTO vulnerabilities (target, host, tool, severity, name, info, cve)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (target, host, tool, severity, name, info, cve))

    def insert_vulnerabilities_bulk(self, target: str, vulns: List[Dict[str, Any]]) -> None:
        """Bulk insert vulnerabilities"""
        data = [
            (target, vuln.get('host', ''), vuln['tool'], vuln['severity'],
             vuln['name'], vuln.get('info', ''), vuln.get('cve'))
            for vuln in vulns
        ]
        self.executemany("""
            INSERT INTO vulnerabilities (target, host, tool, severity, name, info, cve)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, data)

    # ==================== INFRASTRUCTURE ====================

    def insert_infrastructure(self, target: str, host: str, ip: str = None,
                            asn: str = None, org: str = None,
                            cloud_provider: str = None, cdn: str = None,
                            technologies: str = None) -> None:
        """Insert infrastructure data"""
        self.execute("""
            INSERT INTO infrastructure (target, host, ip, asn, org, cloud_provider, cdn, technologies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(target, host) DO UPDATE SET
                ip = COALESCE(excluded.ip, ip),
                asn = COALESCE(excluded.asn, asn),
                org = COALESCE(excluded.org, org),
                cloud_provider = COALESCE(excluded.cloud_provider, cloud_provider),
                cdn = COALESCE(excluded.cdn, cdn),
                technologies = COALESCE(excluded.technologies, technologies)
        """, (target, host, ip, asn, org, cloud_provider, cdn, technologies))

    # ==================== STATISTICS ====================

    def get_stats(self, target: str) -> Dict[str, int]:
        """Get statistics for target in a single query"""
        row = self.fetchone("""
            SELECT
                (SELECT COUNT(*) FROM subdomains WHERE target = ?) as subdomains,
                (SELECT COUNT(*) FROM subdomains WHERE target = ? AND is_alive = 1) as alive_hosts,
                (SELECT COUNT(*) FROM urls WHERE target = ?) as urls,
                (SELECT COUNT(*) FROM vulnerabilities WHERE target = ?) as vulnerabilities,
                (SELECT COUNT(*) FROM vulnerabilities WHERE target = ? AND severity = 'critical') as critical_vulns,
                (SELECT COUNT(*) FROM vulnerabilities WHERE target = ? AND severity = 'high') as high_vulns,
                (SELECT COUNT(*) FROM leaks WHERE target = ?) as leaks,
                (SELECT COUNT(*) FROM ports WHERE target = ?) as open_ports
        """, (target, target, target, target, target, target, target, target))
        return dict(row) if row else {
            'subdomains': 0, 'alive_hosts': 0, 'urls': 0, 'vulnerabilities': 0,
            'critical_vulns': 0, 'high_vulns': 0, 'leaks': 0, 'open_ports': 0
        }

    def close(self):
        """Close database connection"""
        if hasattr(self.local, 'connection') and self.local.connection:
            self.local.connection.close()
            self.local.connection = None


if __name__ == "__main__":
    # Test database creation
    db = DatabaseManager("test_reconx.db")
    db.init_target("example.com")
    print("Database initialized successfully")
    print("Stats:", db.get_stats("example.com"))
