# Week 3-4: Database Layer Foundation
## SQLAlchemy Models & Data Schema

---

## 🎯 Week Goal

**Build the complete data model layer using SQLAlchemy ORM.**

- Create 25+ database models
- Define all relationships (one-to-many, many-to-many)
- Generate comprehensive tests (90%+ coverage)
- Create database migrations
- Establish data integrity constraints

**Expected Outcome:** Solid database foundation for all future work

---

## 📊 Database Design Overview

### Core Concepts

**Scan Process:**
```
1. User creates ScanRun for domain "example.com"
2. Scanner discovers subdomains (discovered_subdomains.txt)
3. For each subdomain:
   - Check if alive (ping, HTTP)
   - Probe ports (Nmap)
   - Analyze web content (screenshots, JS files)
4. For each vulnerability:
   - Store finding
   - Calculate risk
   - Tag with category
5. Generate compliance report
```

### Database Schema (High Level)

```
ScanRun (parent)
├─ Subdomain (many)
│  ├─ PortScan (many)
│  ├─ Vulnerability (many)
│  └─ HTTPHeader (many)
│
├─ DomainTechnology (edges to tech stack)
│  └─ Technology (shared with all domains)
│
├─ DNSRecord (many)
├─ ISPLocation (many)
└─ ComplianceReport (one)
```

---

## 📝 Models to Create (Week 3-4)

### Group 1: Core Scanning Models (5 models)

#### 1. ScanRun
```python
# Core model for a scanning operation
class ScanRun(Base):
    __tablename__ = "scan_runs"
    
    # Fields
    id: Primary key
    domain: Target domain (indexed, unique=False)
    scan_type: "full" | "quick" | "custom"
    status: "pending" | "running" | "completed" | "failed"
    created_at: Datetime
    completed_at: Optional datetime
    
    # Relationships
    subdomains → Subdomain
    vulnerabilities → Vulnerability (direct)
    dns_records → DNSRecord
    technologies → DomainTechnology
    reports → ComplianceReport
```

**Why:** Root of scan operation. Every scan starts here.

#### 2. Subdomain
```python
class Subdomain(Base):
    __tablename__ = "subdomains"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key to ScanRun
    subdomain: String (unique within scan)
    is_alive: Boolean (alive = HTTP/HTTPS responsive)
    discovered_method: "passive" | "active" | "crawl"
    first_seen: Datetime
    last_seen: Datetime
    
    # Relationships
    scan_run → ScanRun
    ports → PortScan
    vulnerabilities → Vulnerability
    http_headers → HTTPHeader
```

**Why:** Each domain may have 10-1000 subdomains. Track each.

#### 3. PortScan
```python
class PortScan(Base):
    __tablename__ = "port_scans"
    
    # Fields
    id: Primary key
    subdomain_id: Foreign key
    port: Integer (1-65535)
    protocol: "tcp" | "udp"
    state: "open" | "closed" | "filtered"
    service: String (HTTP, SSH, SMB, etc)
    version: Optional string (Apache 2.4.41, etc)
    
    # Relationships
    subdomain → Subdomain
    vulnerabilities → Vulnerability
```

**Why:** Track open ports (attack surface)

#### 4. Vulnerability
```python
class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    subdomain_id: Optional foreign key
    vuln_type: String (xss, sqli, weak_cipher, etc)
    severity: Integer 0-100 (CVSS score)
    title: String
    description: Text
    remediation: Text
    discovered_at: Datetime
    cve_ids: JSON array (CVE-2021-1234, etc)
    
    # Relationships
    scan_run → ScanRun
    subdomain → Subdomain (nullable)
    metadata → VulnerabilityMetadata
```

**Why:** Store vulnerabilities and findings

#### 5. HTTPHeader
```python
class HTTPHeader(Base):
    __tablename__ = "http_headers"
    
    # Fields
    id: Primary key
    subdomain_id: Foreign key
    header_name: String (Server, X-Frame-Options, etc)
    header_value: Text
    risk_level: "high" | "medium" | "low" | "info"
    
    # Relationships
    subdomain → Subdomain
```

**Why:** Security-relevant HTTP headers reveal tech stack & misconfigs

---

### Group 2: Intelligence Models (6 models)

#### 6. DomainTechnology
```python
class DomainTechnology(Base):
    __tablename__ = "domain_technologies"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    tech_id: Foreign key to Technology
    detected_at: Datetime
    confidence: Integer 0-100 (how confident in detection)
    
    # Relationships
    scan_run → ScanRun
    technology → Technology
```

**Why:** Many-to-many between scans and technologies (nginx, React, etc)

#### 7. Technology
```python
class Technology(Base):
    __tablename__ = "technologies"
    
    # Fields
    id: Primary key
    name: String (nginx, React, WordPress, etc)
    category: String (Web Server, Framework, CMS)
    version: Optional string
    icon_url: String (for UI)
    
    # Relationships
    domain_technologies → DomainTechnology
    known_vulns → KnownVulnerability
```

**Why:** Shared technology registry (used by millions of scans)

#### 8. KnownVulnerability
```python
class KnownVulnerability(Base):
    __tablename__ = "known_vulnerabilities"
    
    # Fields
    id: Primary key
    technology_id: Foreign key
    cve_id: String (CVE-2021-1234)
    vuln_name: String
    severity: Integer 0-100
    advisory_url: String
    affected_versions: JSON array
    fixed_version: Optional string
    
    # Relationships
    technology → Technology
```

**Why:** Track known vulns for each tech (drives intelligence)

#### 9. DNSRecord
```python
class DNSRecord(Base):
    __tablename__ = "dns_records"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    subdomain: String
    record_type: "A" | "AAAA" | "MX" | "TXT" | "NS" | "CNAME"
    value: String (IP, hostname, etc)
    ttl: Integer
    
    # Relationships
    scan_run → ScanRun
```

**Why:** DNS enumeration reveals domain structure & mail servers

#### 10. ISPLocation
```python
class ISPLocation(Base):
    __tablename__ = "isp_locations"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    ip_address: String (IPv4/IPv6)
    isp_name: String
    country: String
    region: String
    city: String
    latitude: Float
    longitude: Float
    
    # Relationships
    scan_run → ScanRun
```

**Why:** Geolocation of IPs reveals infrastructure distribution

#### 11. ThreatIntelligence
```python
class ThreatIntelligence(Base):
    __tablename__ = "threat_intelligence"
    
    # Fields
    id: Primary key
    indicator_type: "ip" | "domain" | "file_hash"
    indicator_value: String
    severity: Integer 0-100
    source: String (AbuseIPDB, VirusTotal, etc)
    description: Text
    last_updated: Datetime
    
    # Relationships
    isp_locations ← ISP Location (IP-based match)
```

**Why:** External threat intel (malware C2s, botnets, etc)

---

### Group 3: Compliance & Reporting Models (5 models)

#### 12. ComplianceReport
```python
class ComplianceReport(Base):
    __tablename__ = "compliance_reports"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key (unique)
    report_type: "pci-dss" | "hipaa" | "gdpr" | "iso27001"
    generated_at: Datetime
    passed_checks: Integer
    failed_checks: Integer
    overall_score: Integer 0-100
    
    # Relationships
    scan_run → ScanRun
    findings → ComplianceFinding
```

**Why:** Generate compliance reports for regulations

#### 13. ComplianceFinding
```python
class ComplianceFinding(Base):
    __tablename__ = "compliance_findings"
    
    # Fields
    id: Primary key
    report_id: Foreign key
    requirement_id: String (PCI-DSS-6.2, etc)
    control_name: String
    status: "passed" | "failed" | "not-applicable"
    evidence: Text
    remediation: Text
    severity: "critical" | "high" | "medium" | "low"
    
    # Relationships
    report → ComplianceReport
```

**Why:** Individual findings within compliance report

#### 14. RiskScore
```python
class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    calculation_method: String (version of algorithm used)
    critical_count: Integer (CVSS 9-10)
    high_count: Integer (CVSS 7-8.9)
    medium_count: Integer (CVSS 4-6.9)
    low_count: Integer (CVSS 0-3.9)
    overall_score: Integer 0-100
    calculated_at: Datetime
    
    # Relationships
    scan_run → ScanRun
```

**Why:** Calculated risk summary for executive reporting

#### 15. AuditLog
```python
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    # Fields
    id: Primary key
    user: String (username or "system")
    action: String (created_scan, viewed_report, etc)
    entity_type: String (ScanRun, ComplianceReport)
    entity_id: Integer
    details: JSON
    timestamp: Datetime
    
    # Relationships
    None (audit trail only)
```

**Why:** Track who did what for compliance & debugging

---

### Group 4: Asset Change Tracking Models (4 models)

#### 16. AssetSnapshot
```python
class AssetSnapshot(Base):
    __tablename__ = "asset_snapshots"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    snapshot_date: Date (YYYY-MM-DD)
    domain_count: Integer
    subdomain_count: Integer
    open_port_count: Integer
    vulnerability_count: Integer
    critical_vuln_count: Integer
    
    # Relationships
    scan_run → ScanRun
```

**Why:** Track asset growth over time (trending)

#### 17. AssetChange
```python
class AssetChange(Base):
    __tablename__ = "asset_changes"
    
    # Fields
    id: Primary key
    previous_snapshot_id: Foreign key
    current_snapshot_id: Foreign key
    change_type: "new" | "removed" | "modified"
    asset_type: "subdomain" | "port" | "technology" | "vulnerability"
    description: Text
    severity: "critical" | "high" | "medium" | "low"
    
    # Relationships
    previous_snapshot → AssetSnapshot
    current_snapshot → AssetSnapshot
```

**Why:** Highlight new vulnerabilities or removed services

#### 18. ChangeNotification
```python
class ChangeNotification(Base):
    __tablename__ = "change_notifications"
    
    # Fields
    id: Primary key
    asset_change_id: Foreign key
    notification_type: "email" | "webhook" | "slack"
    recipient: String
    sent_at: Datetime
    status: "sent" | "failed" | "pending"
    
    # Relationships
    asset_change → AssetChange
```

**Why:** Alert users to important changes

#### 19. WebsiteSnapshot
```python
class WebsiteSnapshot(Base):
    __tablename__ = "website_snapshots"
    
    # Fields
    id: Primary key
    subdomain_id: Foreign key
    timestamp: Datetime
    http_status: Integer (200, 404, etc)
    content_hash: String (SHA256 of HTML)
    screenshot_url: String (S3 path)
    crawl_depth: Integer (how many links followed)
    
    # Relationships
    subdomain → Subdomain
```

**Why:** Detect website changes (defacement detection)

---

### Group 5: Integration & Metadata Models (5 models)

#### 20. ScannerIntegration
```python
class ScannerIntegration(Base):
    __tablename__ = "scanner_integrations"
    
    # Fields
    id: Primary key
    name: String (Nmap, Burp, Nuclei, Trivy, etc)
    api_endpoint: String (URL or socket path)
    status: "active" | "inactive" | "error"
    last_check_time: Datetime
    error_message: Optional text
    
    # Relationships
    scan_runs → ScanRun (via ScanRunnerMetadata)
```

**Why:** Configure which external scanners to use

#### 21. ScanRunnerMetadata
```python
class ScanRunnerMetadata(Base):
    __tablename__ = "scan_runner_metadata"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    scanner_integration_id: Foreign key
    scanner_name: String (Nmap, Burp, etc)
    executed_at: Datetime
    completed_at: Optional datetime
    status: "pending" | "running" | "completed" | "failed"
    raw_results_file: String (S3 path to raw output)
    
    # Relationships
    scan_run → ScanRun
    scanner → ScannerIntegration
```

**Why:** Track which scanner ran, when, and where results are

#### 22. VulnerabilityMetadata
```python
class VulnerabilityMetadata(Base):
    __tablename__ = "vulnerability_metadata"
    
    # Fields
    id: Primary key
    vulnerability_id: Foreign key
    metadata_key: String (custom_field_name)
    metadata_value: Text (can be JSON)
    
    # Relationships
    vulnerability → Vulnerability
```

**Why:** Extensible metadata for custom vulnerability attributes

#### 23. APIKey
```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    # Fields
    id: Primary key
    user_identifier: String (user_id or email)
    key_hash: String (bcrypt hash of key)
    name: String (My API key)
    created_at: Datetime
    expires_at: Optional datetime
    last_used: Optional datetime
    is_active: Boolean
    
    # Relationships
    None (used for authentication)
```

**Why:** API authentication for external integrations

#### 24. SavedReport
```python
class SavedReport(Base):
    __tablename__ = "saved_reports"
    
    # Fields
    id: Primary key
    scan_run_id: Foreign key
    report_type: String (executive_summary, detailed, compliance, etc)
    format: "pdf" | "html" | "json" | "csv"
    file_path: String (S3 path)
    generated_by: String (user email or system)
    generated_at: Datetime
    
    # Relationships
    scan_run → ScanRun
```

**Why:** Store generated reports

#### 25. ScheduledScan
```python
class ScheduledScan(Base):
    __tablename__ = "scheduled_scans"
    
    # Fields
    id: Primary key
    domain: String
    scan_type: String
    frequency: String (daily | weekly | monthly)
    next_run: Datetime
    last_run: Optional datetime
    is_active: Boolean
    created_by: String
    
    # Relationships
    scan_runs ← ScanRun (one-to-many, filtered by domain)
```

**Why:** Recurring scans for continuous monitoring

---

## 🎯 Tasks for Week 3-4 (25 Atomic Prompts)

### Day 1: Models 1-5 (Core Scanning)

**Prompt 1.1:** Create ScanRun model (PK, fields, docstring)  
**Prompt 1.2:** Create Subdomain model with FK relationship  
**Prompt 1.3:** Create PortScan model  
**Prompt 1.4:** Create Vulnerability model  
**Prompt 1.5:** Create HTTPHeader model  

**Tests:** Unit tests for each model

### Day 2: Models 6-11 (Intelligence)

**Prompt 2.1:** Create DomainTechnology model (many-to-many setup)  
**Prompt 2.2:** Create Technology model  
**Prompt 2.3:** Create KnownVulnerability model  
**Prompt 2.4:** Create DNSRecord model  
**Prompt 2.5:** Create ISPLocation model  
**Prompt 2.6:** Create ThreatIntelligence model  

**Tests:** Unit tests for each model

### Day 3: Models 12-16 (Compliance)

**Prompt 3.1:** Create ComplianceReport model  
**Prompt 3.2:** Create ComplianceFinding model  
**Prompt 3.3:** Create RiskScore model  
**Prompt 3.4:** Create AuditLog model  
**Prompt 3.5:** Create AssetSnapshot model  

**Tests:** Unit tests for each model

### Day 4: Models 17-21 (Changes & Meta)

**Prompt 4.1:** Create AssetChange model  
**Prompt 4.2:** Create ChangeNotification model  
**Prompt 4.3:** Create WebsiteSnapshot model  
**Prompt 4.4:** Create ScannerIntegration model  
**Prompt 4.5:** Create ScanRunnerMetadata model  

**Tests:** Unit tests for each model

### Day 5: Models 22-25 + Integration

**Prompt 5.1:** Create VulnerabilityMetadata model  
**Prompt 5.2:**Create APIKey model  
**Prompt 5.3:** Create SavedReport model  
**Prompt 5.4:** Create ScheduledScan model  
**Prompt 5.5:** Integration tests for all relationships  
**Prompt 5.6:** Full test suite with 90%+ coverage  

**Tests:** Integration tests, relationship tests

---

## 📋 Deliverables by End of Week 4

### Code Deliverables
- ✅ `backend/db/models.py` (400+ lines)
- ✅ `backend/db/schemas.py` (Pydantic models for API)
- ✅ `backend/tests/test_models.py` (400+ lines)
- ✅ `backend/tests/test_relationships.py` (relationship tests)
- ✅ Database migrations (Alembic scripts)

### Testing Deliverables
- ✅ 90%+ test coverage for models
- ✅ All relationships tested
- ✅ All constraints tested
- ✅ All validations tested

### Documentation Deliverables
- ✅ Docstrings on all models
- ✅ Field documentation
- ✅ Relationship documentation
- ✅ `docs/DATABASE_SCHEMA.md` (schema reference)

---

## 🔧 Technical Constants

### Database Configuration
```python
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/reconx"
SQLALCHEMY_ECHO = True  # Log SQL queries during dev
SQLALCHEMY_POOL_SIZE = 20
SQLALCHEMY_MAX_OVERFLOW = 20
```

### Enums to Create
```python
ScanType = Enum("full", "quick", "custom", "custom")
ScanStatus = Enum("pending", "running", "completed", "failed")
VulnerabilityType = Enum("xss", "sqli", "rfi", "etc")
Severity = Enum("critical", "high", "medium", "low")
```

### Indexed Fields
```
scan_runs.domain      # Most queries filter by domain
subdomains.subdomain  # Need fast lookup
subdomains.is_alive   # Filter alive vs dead
vulnerabilities.severity  # Sorting by severity
vulnerability.timestamp   # Time-range queries
```

---

## ✅ Success Criteria

- [ ] All 25 models created with docstrings
- [ ] All relationships defined (FK, back_populates)
- [ ] All constraints defined (unique, nullable, default)
- [ ] 400+ lines in models.py
- [ ] 400+ lines in test_models.py
- [ ] 90%+ test coverage
- [ ] All tests pass
- [ ] Code passes `make lint`
- [ ] Code passes `make type-check`
- [ ] Database migrations generated
- [ ] Documentation complete

---

## 🚀 How to Approach This Week

**Daily Pattern:**
1. Read Day N context (above)
2. Generate models using Cursor Cmd+K
3. Create tests using VS Code Copilot
4. Run full test suite: `make test`
5. Check coverage: `pytest --cov`
6. Fix any issues
7. Commit: `git commit -m "feat: add models X-Y with tests"`

**Parallel Agents:**
- **Agent 1 (Cursor):** Generate models for the day
- **Agent 2 (VS Code):** Write tests simultaneously
- **Agent 3 (Claude):** Design next day's models while current tests run

**Quality Gates (Every Task):**
- [ ] Code has no import errors
- [ ] Type hints 100%
- [ ] Docstrings on all public functions
- [ ] Tests pass with >85% coverage
- [ ] `make lint` passes
- [ ] Single atomic commit

---

## 📚 Example Model (Reference)

Here's what a complete model looks like:

```python
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.db.base import Base

class ScanRun(Base):
    """Represents a single domain scanning operation.
    
    A ScanRun encompasses:
    - Discovery of subdomains
    - Enumeration of active hosts
    - Port scanning
    - Vulnerability detection
    - Compliance checking
    - Reporting
    """
    
    __tablename__ = "scan_runs"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Core Fields
    domain = Column(String(255), nullable=False, index=True)
    scan_type = Column(String(50), default="full")  # full, quick, custom
    status = Column(String(50), default="pending")  # pending, running, completed, failed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    subdomains = relationship("Subdomain", back_populates="scan_run", cascade="all, delete-orphan")
    dns_records = relationship("DNSRecord", back_populates="scan_run", cascade="all, delete-orphan")
    technologies = relationship("DomainTechnology", back_populates="scan_run", cascade="all, delete-orphan")
    compliance_report = relationship("ComplianceReport", back_populates="scan_run", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("idx_domain_created", "domain", "created_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of ScanRun."""
        return f"<ScanRun(id={self.id}, domain={self.domain}, status={self.status})>"
    
    @property
    def duration_seconds(self) -> Optional[int]:
        """Calculate scan duration in seconds."""
        if self.completed_at is None:
            return None
        return int((self.completed_at - self.created_at).total_seconds())
```

Use this as template for other models!

---

## 🎬 Ready to Start?

1. Read this entire document (15 min)
2. Read `prompts-design/SYSTEM_PROMPTS.md` (understanding requirements)
3. Open `prompts-design/week-3-4/PROMPTS.md` for actual prompts
4. Start with Prompt 1.1 using Cursor IDE
5. Execute → Verify → Commit → Next

**Week 3-4 is your gateway to having a real, functional data layer!** 🚀
