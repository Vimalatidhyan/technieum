# Complete Project Prompts - Sequential Execution
## ReconX Enterprise v2.0 - All Prompts for Single Agent

---

## 📖 How to Use This File

**This file contains ALL prompts needed to build ReconX Enterprise v2.0 from start to finish.**

### Instructions:
1. Read each prompt completely
2. Copy the entire prompt (including context section)
3. Paste into your AI tool (Cursor IDE recommended: Cmd+K, or Claude)
4. Wait for code generation
5. Copy generated code to the specified file
6. Run verification commands (listed after each prompt)
7. Move to next prompt when verification passes
8. Commit changes: `git commit -m "feat: <description>"`

### Tools to Use:
- **Cursor IDE (Recommended):** Cmd+K for chat (best for code generation)
- **Claude:** Paste into https://claude.ai (good for complex logic)
- **VS Code Copilot:** For quick fixes if needed

### Verification Pattern (Every Task):
```bash
# 1. Test imports
python -c "from backend.db.models import YourClass"

# 2. Type check
mypy backend/

# 3. Run tests
make test

# 4. Check coverage
pytest --cov=backend backend/tests/

# 5. Format code
make lint

# 6. Commit
git commit -m "feat: <what you built>"
```

---

## 🚀 WEEK 1-2: Foundation Phase (ALREADY COMPLETE)

**Status:** ✅ Complete - Foundation already built  
**Files Already Created:**
- Docker Compose stack
- Makefile with 20+ commands
- requirements.txt (87 packages)
- GitHub Actions CI/CD
- Complete documentation

**What to Do:**
```bash
# Start the stack
docker-compose up -d

# Verify all 8 services running
docker-compose ps

# You should see 8 services: UP
```

---

## 💾 WEEK 3-4: Database Layer
### Start Monday Morning - Complete by Friday

---

### PROMPT 1: Create ScanRun Model

**File to Create:** `backend/db/models.py`

```
[SYSTEM CONTEXT]
You are building ReconX Enterprise - a professional vulnerability scanning platform.
Follow these REQUIREMENTS for ALL code:
- Type hints on 100% of functions and class attributes
- Docstrings on all public classes/methods (Google style)
- PEP 8 style (88 char lines, use black formatting)
- All fields must be typed and nullable status specified
- Use SQLAlchemy ORM for database models
- Include __repr__ method for debugging

[PROJECT CONTEXT]
- Database: PostgreSQL with SQLAlchemy ORM
- Framework: FastAPI + SQLAlchemy
- Location: backend/db/models.py
- Base class: from backend.db.base import Base

[TASK]
Create the ScanRun model - represents a single domain scanning operation.

EXACT REQUIREMENTS:
1. Class name: ScanRun(Base)
2. Tablename: "scan_runs"
3. Fields (in order):
   - id: Integer, primary_key=True
   - domain: String(255), nullable=False, indexed, unique per run
   - scan_type: String(50), default="full"  [values: full, quick, custom]
   - status: String(50), default="pending"  [values: pending, running, completed, failed]
   - created_at: DateTime, default=datetime.utcnow, indexed
   - completed_at: DateTime, nullable=True
4. Include docstring explaining: "Represents a single domain scanning operation"
5. Include __repr__ method: "return f'<ScanRun(id={self.id}, domain={self.domain})>'"
6. Add Index on (domain, created_at)

EXAMPLE STRUCTURE:
class ScanRun(Base):
    """Represents..."""
    __tablename__ = "scan_runs"
    id = Column(...)
    domain = Column(...)
    # ... other fields
    def __repr__(self):
        ...

SUCCESS CRITERIA:
✓ Model has all 6 fields
✓ All fields are typed
✓ Docstring present and explains purpose
✓ __repr__ method works
✓ Can import: from backend.db.models import ScanRun
✓ No type errors from mypy
```

**Verification:**
```bash
# Test import
python -c "from backend.db.models import ScanRun; print('✓ ScanRun imported')"

# Type check
mypy backend/db/models.py

# Should show: Success: no issues found
```

**After verification: `git commit -m "feat: add ScanRun model"`**

---

### PROMPT 2: Create Subdomain Model

**File:** `backend/db/models.py` (add to existing file)

```
[SYSTEM CONTEXT - See PROMPT 1 for requirements]

[TASK]
Add the Subdomain model to backend/db/models.py

EXACT REQUIREMENTS:
1. Class name: Subdomain(Base)
2. Tablename: "subdomains"
3. Fields:
   - id: Integer, primary_key=True
   - scan_run_id: Integer, ForeignKey("scan_runs.id"), nullable=False
   - subdomain: String(255), nullable=False, indexed
   - is_alive: Boolean, default=False
   - discovered_method: String(50)  [values: passive, active, crawl]
   - first_seen: DateTime, default=datetime.utcnow
   - last_seen: DateTime, nullable=True
4. Relationships:
   - scan_run: relationship("ScanRun", back_populates="subdomains")
5. Docstring: "Represents a discovered subdomain of a scanned domain"
6. Include __repr__ method

SUCCESS CRITERIA:
✓ 7 fields all defined
✓ Foreign key to ScanRun correct
✓ Relationship with back_populates
✓ Can import: from backend.db.models import Subdomain
✓ No type errors
```

**Verification:**
```bash
python -c "from backend.db.models import Subdomain, ScanRun; print('✓ Models imported')"
mypy backend/db/models.py
# Then add relationship to ScanRun:
# subdomains = relationship("Subdomain", back_populates="scan_run", cascade="all, delete-orphan")
```

**After verification: `git commit -m "feat: add Subdomain model with ScanRun relationship"`**

---

### PROMPT 3: Create PortScan Model

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same requirements as PROMPT 1

[TASK]
Add PortScan model to backend/db/models.py

EXACT REQUIREMENTS:
1. Class name: PortScan(Base)
2. Tablename: "port_scans"
3. Fields:
   - id: Integer, primary_key=True
   - subdomain_id: Integer, ForeignKey("subdomains.id"), nullable=False
   - port: Integer, nullable=False (1-65535)
   - protocol: String(10), default="tcp"  [tcp or udp]
   - state: String(20)  [open, closed, filtered]
   - service: String(50), nullable=True  [HTTP, SSH, SMB, etc]
   - version: String(100), nullable=True
4. Relationships:
   - subdomain: relationship("Subdomain", back_populates="ports")
5. Docstring: "Represents an open/scanned port on a subdomain"
6. Index on (subdomain_id, port)

SUCCESS CRITERIA:
✓ 7 fields defined
✓ Foreign key correct
✓ Relationship setup
✓ Can import without errors
```

**Verification:**
```bash
python -c "from backend.db.models import PortScan; print('✓ OK')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add PortScan model"`**

---

### PROMPT 4: Create Vulnerability Model

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same requirements as PROMPT 1

[TASK]
Add Vulnerability model

EXACT REQUIREMENTS:
1. Class name: Vulnerability(Base)
2. Tablename: "vulnerabilities"
3. Fields:
   - id: Integer, primary_key=True
   - scan_run_id: Integer, ForeignKey("scan_runs.id"), nullable=False
   - subdomain_id: Integer, ForeignKey("subdomains.id"), nullable=True
   - vuln_type: String(50), nullable=False  [xss, sqli, weak_cipher, etc]
   - severity: Integer, nullable=False  [0-100 CVSS score]
   - title: String(255), nullable=False
   - description: Text, nullable=False
   - remediation: Text, nullable=True
   - discovered_at: DateTime, default=datetime.utcnow
   - cve_ids: JSON (array of CVE-2021-1234 etc)  [nullable]
4. Relationships:
   - scan_run: relationship("ScanRun", back_populates="vulnerabilities")
   - subdomain: relationship("Subdomain", back_populates="vulnerabilities") [nullable]
5. Index on severity (for sorting)

SUCCESS CRITERIA:
✓ All 10 fields defined
✓ Foreign keys working
✓ JSON field for CVE array
✓ Relationships configured
```

**Verification:**
```bash
python -c "from backend.db.models import Vulnerability; print('✓ OK')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add Vulnerability model with CVSS tracking"`**

---

### PROMPT 5: Create HTTPHeader Model

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same requirements

[TASK]
Add HTTPHeader model - tracks security-relevant HTTP headers

EXACT REQUIREMENTS:
1. Class name: HTTPHeader(Base)
2. Tablename: "http_headers"
3. Fields:
   - id: Integer, primary_key=True
   - subdomain_id: Integer, ForeignKey("subdomains.id"), nullable=False
   - header_name: String(100), nullable=False  [Server, X-Frame-Options, etc]
   - header_value: Text, nullable=False
   - risk_level: String(20), default="info"  [high, medium, low, info]
4. Relationships:
   - subdomain: relationship("Subdomain", back_populates="http_headers")
5. Index on (subdomain_id, header_name)

SUCCESS CRITERIA:
✓ 5 fields defined
✓ Relationship to Subdomain
✓ Can import and use
```

**Verification:**
```bash
python -c "from backend.db.models import HTTPHeader; print('✓ OK')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add HTTPHeader model for security headers"`**

---

### PROMPT 6: Add Relationships to Models

**File:** `backend/db/models.py` (update ScanRun class)

```
[TASK]
Update ScanRun model to add all relationships

ADD to ScanRun class (after id, domain, scan_type, status, created_at, completed_at fields):

    # Relationships
    subdomains = relationship("Subdomain", back_populates="scan_run", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="scan_run", cascade="all, delete-orphan")

ADD to Subdomain class (after fields):

    # Relationships  
    scan_run = relationship("ScanRun", back_populates="subdomains")
    ports = relationship("PortScan", back_populates="subdomain", cascade="all, delete-orphan")
    vulnerabilities = relationship("Vulnerability", back_populates="subdomain", cascade="all, delete-orphan")
    http_headers = relationship("HTTPHeader", back_populates="subdomain", cascade="all, delete-orphan")

ADD to PortScan class (after fields):

    subdomain = relationship("Subdomain", back_populates="ports")

ADD to Vulnerability class (after fields):

    scan_run = relationship("ScanRun", back_populates="vulnerabilities")
    subdomain = relationship("Subdomain", back_populates="vulnerabilities")

ADD to HTTPHeader class (after fields):

    subdomain = relationship("Subdomain", back_populates="http_headers")

SUCCESS CRITERIA:
✓ All relationships use back_populates
✓ Cascade delete configured where needed
✓ No circular imports
✓ mypy shows no errors
```

**Verification:**
```bash
mypy backend/db/models.py
python -c "from backend.db.models import ScanRun, Subdomain, PortScan, Vulnerability, HTTPHeader; print('✓ All models imported')"
```

**Commit: `git commit -m "feat: add relationships between database models"`**

---

### PROMPT 7: Create Database Tests for Models

**File to Create:** `backend/tests/test_models.py`

```
[SYSTEM CONTEXT]
You are creating comprehensive pytest tests for database models.
Requirements:
- Use pytest fixtures for setup
- Test both creation and validation
- Include success and failure cases
- Aim for 90%+ coverage
- Use conftest.py for shared fixtures
- Mockdata where needed

[TASK]
Create comprehensive test suite for models

TESTS TO CREATE:

1. test_scanrun_creation()
   - Create ScanRun with domain="example.com"
   - Assert domain, status="pending", created_at is not None

2. test_scanrun_invalid_missing_domain()
   - Try to create ScanRun without domain
   - Should raise error or fail validation

3. test_subdomain_creation()
   - Create Subdomain with scan_run_id, subdomain="www.example.com"
   - Assert created successfully

4. test_subdomain_relationships()
   - Create ScanRun, add Subdomain
   - Assert scan_run.subdomains contains the subdomain

5. test_port_scan_creation()
   - Create PortScan with port=80, protocol="tcp"
   - Assert state defaults correctly

6. test_vulnerability_creation()
   - Create Vulnerability with severity=85, vuln_type="xss"
   - Assert severity in range 0-100

7. test_vulnerability_cve_tracking()
   - Create Vulnerability with cve_ids=["CVE-2021-1234", "CVE-2022-5678"]
   - Assert CVE array stored correctly

8. test_http_header_creation()
   - Create HTTPHeader with header_name="Server", header_value="Apache"
   - Assert risk_level defaults to "info"

9. test_cascading_deletes()
   - Create ScanRun with Subdomains
   - Delete ScanRun
   - Assert Subdomains deleted too

10. test_repr_methods()
    - Create model instances
    - Call __repr__()
    - Assert returns valid string representation

SUCCESS CRITERIA:
✓ 10+ test functions
✓ All models tested
✓ Both success and failure cases
✓ Relationships verified
✓ Cascade delete tested
✓ All tests pass: pytest backend/tests/test_models.py

USE THIS PATTERN:

import pytest
from datetime import datetime
from backend.db.models import ScanRun, Subdomain, PortScan, Vulnerability, HTTPHeader

def test_scanrun_creation():
    """Test creating a ScanRun instance."""
    scan = ScanRun(domain="example.com", scan_type="full")
    assert scan.domain == "example.com"
    assert scan.status == "pending"
    assert isinstance(scan.created_at, datetime)

# ... continue with other tests
```

**Verification:**
```bash
# Run tests
pytest backend/tests/test_models.py -v

# Check coverage
pytest backend/tests/test_models.py --cov=backend.db.models

# Should show >85% coverage
```

**Commit: `git commit -m "feat: add comprehensive model tests with 90%+ coverage"`**

---

### PROMPT 8: Create Database Schemas (Pydantic Models)

**File to Create:** `backend/db/schemas.py`

```
[SYSTEM CONTEXT]
You are creating Pydantic models for API validation and serialization.
Requirements:
- Use FastAPI/Pydantic BaseModel
- Map to database models
- Include validation
- Use Config class for ORM mode

[TASK]
Create Pydantic schemas for all models

SCHEMAS TO CREATE:

1. ScanRunCreate
   - Fields: domain, scan_type (optional, default="full")
   - Validation: domain required, 5-255 chars

2. ScanRunResponse
   - Fields: id, domain, scan_type, status, created_at, completed_at
   - from_attributes = True (ORM mode)

3. SubdomainCreate
   - Fields: scan_run_id, subdomain, discovered_method
   - Validation: subdomain required

4. SubdomainResponse
   - Fields: id, scan_run_id, subdomain, is_alive, discovered_method, first_seen

5. PortScanCreate
   - Fields: subdomain_id, port, protocol, state, service, version

6. PortScanResponse
   - Fields: id, subdomain_id, port, protocol, state, service, version

7. VulnerabilityCreate
   - Fields: scan_run_id, subdomain_id, vuln_type, severity, title, description, remediation, cve_ids

8. VulnerabilityResponse
   - Fields: all from create + id, discovered_at

9. HTTPHeaderCreate
   - Fields: subdomain_id, header_name, header_value, risk_level

10. HTTPHeaderResponse
    - Fields: all from create + id

USE THIS PATTERN:

from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List

class ScanRunCreate(BaseModel):
    domain: str = Field(..., min_length=5, max_length=255)
    scan_type: str = "full"
    
    @validator('scan_type')
    def validate_scan_type(cls, v):
        if v not in ['full', 'quick', 'custom']:
            raise ValueError('Invalid scan_type')
        return v

class ScanRunResponse(ScanRunCreate):
    id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ... continue for all models
```

**Verification:**
```bash
# Test imports
python -c "from backend.db.schemas import ScanRunCreate, ScanRunResponse; print('✓ Schemas imported')"

# Type check
mypy backend/db/schemas.py

# No errors expected
```

**Commit: `git commit -m "feat: add Pydantic schemas for API validation"`**

---

### PROMPT 9: Create conftest.py with Fixtures

**File to Create:** `backend/tests/conftest.py`

```
[SYSTEM CONTEXT]
You are creating pytest fixtures for all tests.
Requirements:
- Use @pytest.fixture
- Create shared database session
- Create sample data
- Clean up after tests

[TASK]
Create fixtures for testing

FIXTURES TO CREATE:

1. @pytest.fixture
   def test_db_session():
       """Create a test database session."""
       # Create in-memory SQLite or test PostgreSQL
       # Yield session
       # Cleanup after test

2. @pytest.fixture
   def sample_scan_run(test_db_session):
       """Create a sample ScanRun for testing."""
       scan = ScanRun(domain="example.com", scan_type="full")
       test_db_session.add(scan)
       test_db_session.commit()
       return scan

3. @pytest.fixture
   def sample_subdomain(test_db_session, sample_scan_run):
       """Create a sample Subdomain."""
       subdomain = Subdomain(
           scan_run_id=sample_scan_run.id,
           subdomain="www.example.com",
           discovered_method="active"
       )
       test_db_session.add(subdomain)
       test_db_session.commit()
       return subdomain

4. @pytest.fixture
   def sample_port_scan(test_db_session, sample_subdomain):
       """Create a sample PortScan."""
       port = PortScan(
           subdomain_id=sample_subdomain.id,
           port=80,
           protocol="tcp",
           state="open",
           service="HTTP"
       )
       test_db_session.add(port)
       test_db_session.commit()
       return port

USE THIS PATTERN:

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.base import Base
from backend.db.models import ScanRun, Subdomain, PortScan

@pytest.fixture
def test_db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def sample_scan_run(test_db_session):
    scan = ScanRun(domain="test.example.com", scan_type="quick")
    test_db_session.add(scan)
    test_db_session.commit()
    return scan

# ... continue with other fixtures
```

**Verification:**
```bash
pytest backend/tests/ -v

# Should be able to use fixtures
```

**Commit: `git commit -m "feat: add pytest fixtures for database testing"`**

---

### PROMPT 10: Create More Database Models (Intelligence Layer)

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same style and requirements as previous prompts

[TASK]
Add 6 intelligence models to backend/db/models.py:

1. Technology Model
   - id, name (unique), category, version, icon_url
   - Docstring: "Represents a technology (nginx, React, etc)"

2. DomainTechnology Model
   - id, scan_run_id (FK), tech_id (FK), detected_at, confidence (0-100)
   - Relationships linking ScanRun and Technology

3. KnownVulnerability Model
   - id, technology_id (FK), cve_id, vuln_name, severity, advisory_url
   - affected_versions (JSON), fixed_version

4. DNSRecord Model
   - id, scan_run_id (FK), subdomain, record_type (A, AAAA, MX, etc)
   - value, ttl

5. ISPLocation Model
   - id, scan_run_id (FK), ip_address, isp_name, country, region, city
   - latitude, longitude

6. ThreatIntelligence Model
   - id, indicator_type (ip, domain, hash), indicator_value, severity
   - source, description, last_updated

REQUIREMENTS:
✓ All models inherit from Base
✓ All have proper docstrings
✓ Foreign keys configured
✓ Relationships set up where applicable
✓ All fields typed
✓ Indexes on frequently-queried fields

SUCCESS CRITERIA:
✓ 6 models created
✓ All relationships working
✓ Can import all models
✓ mypy shows no errors
```

**Verification:**
```bash
python -c "from backend.db.models import Technology, DomainTechnology, KnownVulnerability, DNSRecord, ISPLocation, ThreatIntelligence; print('✓ All imported')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add intelligence layer models (Technology, DNS, ISP, Threat Intel)"`**

---

### PROMPT 11: Create Compliance & Reporting Models

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same as previous

[TASK]
Add 4 compliance models:

1. RiskScore Model
   - id, scan_run_id (FK), calculation_method, critical_count, high_count
   - medium_count, low_count, overall_score (0-100), calculated_at

2. ComplianceReport Model
   - id, scan_run_id (FK, unique), report_type (pci-dss, hipaa, gdpr, iso27001)
   - generated_at, passed_checks, failed_checks, overall_score

3. ComplianceFinding Model
   - id, report_id (FK), requirement_id, control_name, status
   - evidence, remediation, severity

4. AuditLog Model
   - id, user (username), action, entity_type, entity_id, details (JSON)
   - timestamp

REQUIREMENTS:
✓ All models complete
✓ Relationships configured
✓ Cascade deletes where appropriate
✓ Indexes on frequently filtered fields

SUCCESS CRITERIA:
✓ 4 models created
✓ All fully typed
✓ All relationships working
✓ No mypy errors
```

**Verification:**
```bash
python -c "from backend.db.models import RiskScore, ComplianceReport, ComplianceFinding, AuditLog; print('✓ OK')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add compliance reporting models (RiskScore, ComplianceReport, AuditLog)"`**

---

### PROMPT 12: Create Asset Tracking Models

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same requirements

[TASK]
Add asset tracking models:

1. AssetSnapshot Model
   - id, scan_run_id (FK), snapshot_date, domain_count, subdomain_count
   - open_port_count, vulnerability_count, critical_vuln_count

2. AssetChange Model
   - id, previous_snapshot_id (FK), current_snapshot_id (FK)
   - change_type (new, removed, modified), asset_type, description, severity

3. ChangeNotification Model
   - id, asset_change_id (FK), notification_type (email, webhook, slack)
   - recipient, sent_at, status (sent, failed, pending)

4. WebsiteSnapshot Model
   - id, subdomain_id (FK), timestamp, http_status, content_hash
   - screenshot_url, crawl_depth

REQUIREMENTS:
✓ All 4 models created
✓ Foreign keys correct
✓ Relationships configured
✓ All typed

SUCCESS CRITERIA:
✓ Models created
✓ No import errors
✓ mypy clean
```

**Verification:**
```bash
python -c "from backend.db.models import AssetSnapshot, AssetChange, ChangeNotification, WebsiteSnapshot; print('✓ OK')"
mypy backend/db/models.py
```

**Commit: `git commit -m "feat: add asset change tracking models"`**

---

### PROMPT 13: Create Integration & Metadata Models

**File:** `backend/db/models.py` (add to existing)

```
[SYSTEM CONTEXT]
Same requirements

[TASK]
Add integration models:

1. ScannerIntegration Model
   - id, name (Nmap, Burp, Nuclei, etc), api_endpoint, status (active, inactive, error)
   - last_check_time, error_message

2. ScanRunnerMetadata Model
   - id, scan_run_id (FK), scanner_integration_id (FK), scanner_name
   - executed_at, completed_at, status, raw_results_file

3. VulnerabilityMetadata Model
   - id, vulnerability_id (FK), metadata_key, metadata_value (Text)

4. APIKey Model
  - id, user_identifier, key_hash (bcrypt), name, created_at, expires_at
   - last_used, is_active

5. SavedReport Model
   - id, scan_run_id (FK), report_type, format (pdf, html, json, csv)
   - file_path, generated_by, generated_at

6. ScheduledScan Model
   - id, domain, scan_type, frequency (daily, weekly, monthly)
   - next_run, last_run, is_active, created_by

REQUIREMENTS:
✓ All 6 models created
✓ Complete with relationships
✓ All typed

SUCCESS CRITERIA:
✓ Can import all
✓ All relationships work
✓ mypy clean
```

**Verification:**
```bash
python -c "from backend.db.models import ScannerIntegration, ScanRunnerMetadata, VulnerabilityMetadata, APIKey, SavedReport, ScheduledScan; print('✓ OK')"
mypy backend/db/models.py

# Check total models
wc -l backend/db/models.py
# Should be 400-500+ lines
```

**Commit: `git commit -m "feat: add final integration and metadata models (25 total models complete)"`**

---

### PROMPT 14: Create Database Migrations with Alembic

```
[TASK]
Create database migrations using Alembic

STEPS:

1. Initialize Alembic (if not done):
   alembic init alembic

2. Update alembic.ini:
   sqlalchemy.url = postgresql://user:password@localhost/reconx

3. Update alembic/env.py:
   from backend.db.base import Base
   target_metadata = Base.metadata

4. Create first migration:
   alembic revision --autogenerate -m "Initial schema with 25 models"

5. Review alembic/versions/xxxx_initial_schema.py:
   - Verify all 25 models included
   - Check relationships
   - Verify constraints

6. Apply migration:
   alembic upgrade head

SUCCESS CRITERIA:
✓ All 25 tables created in PostgreSQL
✓ Foreign keys set up
✓ Indexes created
✓ No schema errors

VERIFICATION:
```bash
# Connect to PostgreSQL and check
psql reconx -l

# Or using pgAdmin
# Connect to localhost:5050
# Navigate to reconx database
# Verify all tables exist
```

**Commit: `git commit -m "feat: add Alembic migrations for schema creation"`**

---

### PROMPT 15: Write Full Integration Test Suite

**File:** `backend/tests/test_integration.py`

```
[TASK]
Create integration tests covering model relationships

TESTS:

1. test_full_scan_workflow():
   - Create ScanRun
   - Add Subdomain
   - Add PortScan to subdomain
   - Add Vulnerability
   - Verify all relationships work

2. test_scan_run_cascade_delete():
   - Create ScanRun with Subdomains
   - Delete ScanRun
   - Verify all child records deleted

3. test_technology_tracking():
   - Create ScanRun
   - Add DomainTechnology
   - Add Technology
   - Add KnownVulnerability
   - Verify relationships

4. test_compliance_report_generation():
   - Create ScanRun
   - Create RiskScore
   - Create ComplianceReport
   - Add ComplianceFindings
   - Verify report complete

5. test_asset_change_tracking():
   - Create AssetSnapshot
   - Create new AssetSnapshot
   - Create AssetChange
   - Add ChangeNotification
   - Verify tracking

SUCCESS CRITERIA:
✓ 5+ integration tests
✓ All tests passing
✓ Coverage >85%
✓ Real-world workflows tested

VERIFICATION:
```bash
pytest backend/tests/test_integration.py -v
pytest backend/tests/ --cov=backend --cov-report=term
# Should show >85% coverage
```

**Commit: `git commit -m "feat: add integration tests covering all model relationships"`**

---

## Summary: Week 3-4 Deliverables

By end of Friday:
- ✅ 25 database models created
- ✅ All models fully typed with docstrings
- ✅ All relationships configured
- ✅ 400+ lines in models.py
- ✅ 400+ lines in tests
- ✅ 90%+ test coverage
- ✅ Alembic migrations created
- ✅ 15 git commits with semantic messages
- ✅ Database schema deployed

**Ready for Week 5!**

---

## 🏗️ WEEK 5-6: Backend Orchestrator
### Sequential Execution - Single Agent

---

### PROMPT 16: Create Orchestrator Base Class

**File to Create:** `backend/orchestrator/base.py`

```
[SYSTEM CONTEXT]
Building the orchestrator - coordinates scanning activities
Requirements same as before: type hints 100%, docstrings, PEP 8

[TASK]
Create abstract base class for orchestrator

CLASS DEFINITION:

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

class AbstractOrchestrator(ABC):
    """Base class for all scanning orchestrators."""
    
    def __init__(self, scan_run_id: int):
        """Initialize orchestrator with scan_run_id."""
        self.scan_run_id = scan_run_id
        self.status = "initialized"
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.results: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """Execute the orchestration. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def validate_inputs(self) -> bool:
        """Validate that scan can proceed."""
        pass
    
    def update_status(self, status: str) -> None:
        """Update orchestrator status."""
        self.status = status
        # Log status update
    
    def record_result(self, key: str, value: Any) -> None:
        """Record a result from scanning."""
        self.results[key] = value
    
    async def start(self) -> None:
        """Start the orchestration."""
        self.start_time = datetime.utcnow()
        self.update_status("running")
    
    async def finish(self) -> None:
        """Finish the orchestration."""
        self.end_time = datetime.utcnow()
        self.update_status("completed")
    
    def get_duration(self) -> Optional[int]:
        """Get duration in seconds."""
        if self.start_time and self.end_time:
            return int((self.end_time - self.start_time).total_seconds())
        return None

REQUIREMENTS:
✓ Abstract class with ABC
✓ Abstract methods marked with @abstractmethod
✓ All async method handling
✓ Type hints on all parameters
✓ Comprehensive docstrings

SUCCESS CRITERIA:
✓ Can import: from backend.orchestrator.base import AbstractOrchestrator
✓ Cannot instantiate directly (abstract)
✓ mypy shows no errors
```

**Verification:**
```bash
python -c "from backend.orchestrator.base import AbstractOrchestrator; print('✓ Base class imported')"
mypy backend/orchestrator/base.py
```

**Commit: `git commit -m "feat: add abstract orchestrator base class"`**

---

### PROMPT 17: Create Phase 1 Discovery Orchestrator

**File to Create:** `backend/orchestrator/phase1.py`

```
[SYSTEM CONTEXT]
Implementing Phase 1: Discovery (find all domains, subdomains, IPs)
Extends AbstractOrchestrator from base.py

[TASK]
Create Phase1Orchestrator class

IMPLEMENTATION:

from typing import Dict, List, Any
from backend.orchestrator.base import AbstractOrchestrator
from backend.db.models import ScanRun, Subdomain
from datetime import datetime

class Phase1Orchestrator(AbstractOrchestrator):
    """Phase 1: Discovery - find all targets."""
    
    def __init__(self, scan_run_id: int):
        """Initialize phase 1 orchestrator."""
        super().__init__(scan_run_id)
        self.phase_name = "Discovery"
        self.discovered_subdomains: List[str] = []
        self.discovered_ips: List[str] = []
    
    def validate_inputs(self) -> bool:
        """Validate scan can proceed."""
        # Check domain is valid
        # Check API keys available
        # Return True/False
        return True
    
    async def execute(self) -> Dict[str, Any]:
        """Execute discovery phase."""
        await self.start()
        
        try:
            # Step 1: Passive subdomain enumeration
            passive_subs = await self._passive_enumeration()
            self.discovered_subdomains.extend(passive_subs)
            self.record_result("passive_subdomains", len(passive_subs))
            
            # Step 2: Active subdomain enumeration
            active_subs = await self._active_enumeration()
            self.discovered_subdomains.extend(active_subs)
            self.record_result("active_subdomains", len(active_subs))
            
            # Step 3: DNS resolution
            ips = await self._dns_resolution()
            self.discovered_ips.extend(ips)
            self.record_result("resolved_ips", len(ips))
            
            # Step 4: Save to database
            await self._save_discoveries()
            
            await self.finish()
            return self.results
        
        except Exception as e:
            self.update_status("failed")
            self.record_result("error", str(e))
            raise
    
    async def _passive_enumeration(self) -> List[str]:
        """Run passive enumeration (using APIs)."""
        # Call external APIs for subdomain enumeration
        # Return list of discovered subdomains
        return []
    
    async def _active_enumeration(self) -> List[str]:
        """Run active enumeration (brute force)."""
        # Brute force common subdomains
        # Return new subdomains
        return []
    
    async def _dns_resolution(self) -> List[str]:
        """Resolve discovered subdomains."""
        # DNS resolve all discovered subdomains
        # Return IPs
        return []
    
    async def _save_discoveries(self) -> None:
        """Save discoveries to database."""
        # Create Subdomain records
        # Create ISPLocation records
        pass

REQUIREMENTS:
✓ Inherits from AbstractOrchestrator
✓ Implements execute() and validate_inputs()
✓ All methods async
✓ Proper error handling
✓ Records results as it goes

SUCCESS CRITERIA:
✓ Can import: from backend.orchestrator.phase1 import Phase1Orchestrator
✓ Can instantiate: orchestrator = Phase1Orchestrator(scan_run_id=1)
✓ mypy shows no errors
```

**Verification:**
```bash
python -c "from backend.orchestrator.phase1 import Phase1Orchestrator; print('✓ Phase1 imported')"
mypy backend/orchestrator/phase1.py
```

**Commit: `git commit -m "feat: add Phase 1 Discovery orchestrator"`**

---

### PROMPT 18: Create Phase 2 Intelligence Orchestrator

**File to Create:** `backend/orchestrator/phase2.py`

```
[TASK]
Create Phase2Orchestrator - gather intelligence about discovered hosts

CLASS:

from backend.orchestrator.base import AbstractOrchestrator
from typing import Dict, List, Any

class Phase2Orchestrator(AbstractOrchestrator):
    """Phase 2: Intelligence Gathering."""
    
    def __init__(self, scan_run_id: int):
        super().__init__(scan_run_id)
        self.phase_name = "Intelligence"
        self.technologies_found: List[str] = []
        self.dns_records: Dict[str, List] = {}
    
    def validate_inputs(self) -> bool:
        """Requires Phase 1 to be complete."""
        return True
    
    async def execute(self) -> Dict[str, Any]:
        """Execute intelligence gathering."""
        await self.start()
        
        try:
            # Collect existing subdomains from DB
            subdomains = await self._get_subdomains()
            
            # For each subdomain
            for subdomain in subdomains:
                # Get HTTP headers
                headers = await self._get_http_headers(subdomain)
                
                # Detect technologies  
                techs = await self._detect_technologies(subdomain)
                self.technologies_found.extend(techs)
                
                # Get DNS records
                dns = await self._get_dns_records(subdomain)
                self.dns_records[subdomain] = dns
            
            # Save all intelligence to database
            await self._save_intelligence()
            
            await self.finish()
            return self.results
        
        except Exception as e:
            self.update_status("failed")
            self.record_result("error", str(e))
            raise
    
    async def _get_subdomains(self) -> List[str]:
        """Get subdomains from database."""
        return []
    
    async def _get_http_headers(self, subdomain: str) -> Dict[str, str]:
        """Fetch HTTP headers from subdomain."""
        return {}
    
    async def _detect_technologies(self, subdomain: str) -> List[str]:
        """Detect web technologies used."""
        return []
    
    async def _get_dns_records(self, subdomain: str) -> Dict[str, List]:
        """Get DNS records for subdomain."""
        return {}
    
    async def _save_intelligence(self) -> None:
        """Save to database."""
        pass

REQUIREMENTS:
✓ Inherits from AbstractOrchestrator
✓ All async methods
✓ Type hints everywhere
✓ Saves results to DB
```

**Verification:**
```bash
python -c "from backend.orchestrator.phase2 import Phase2Orchestrator; print('✓ Phase2 imported')"
mypy backend/orchestrator/
```

**Commit: `git commit -m "feat: add Phase 2 Intelligence orchestrator"`**

---

### PROMPT 19: Create Phase 3 Content Scanning Orchestrator

**File to Create:** `backend/orchestrator/phase3.py`

```
[TASK]
Create Phase3Orchestrator - scan for web content (JS files, etc)

IMPLEMENTATION following same pattern as Phase 2

class Phase3Orchestrator(AbstractOrchestrator):
    """Phase 3: Content Scanning."""
    
    async def execute(self) -> Dict[str, Any]:
        """Scan for content."""
        await self.start()
        
        try:
            # Get alive subdomains
            subdomains = await self._get_alive_subdomains()
            
            for subdomain in subdomains:
                # Screenshot
                screenshot = await self._take_screenshot(subdomain)
                
                # Crawl JavaScript files
                js_files = await self._crawl_js_files(subdomain)
                
                # Crawl URLs
                urls = await self._crawl_urls(subdomain)
                
                # Brute force directories
                dirs = await self._brute_force_dirs(subdomain)
            
            await self._save_content()
            await self.finish()
            return self.results
        
        except Exception as e:
            self.update_status("failed")
            raise
    
    async def _get_alive_subdomains(self) -> List[str]:
        """Get only alive subdomains from DB."""
        return []
    
    async def _take_screenshot(self, subdomain: str) -> str:
        """Take screenshot of subdomain."""
        return ""
    
    async def _crawl_js_files(self, subdomain: str) -> List[str]:
        """Find JavaScript files."""
        return []
    
    async def _crawl_urls(self, subdomain: str) -> List[str]:
        """Crawl and find URLs."""
        return []
    
    async def _brute_force_dirs(self, subdomain: str) -> List[str]:
        """Brute force directories."""
        return []
    
    async def _save_content(self) -> None:
        """Save to database."""
        pass

REQUIREMENTS:
✓ Same pattern as Phase 1 and 2
✓ Inherits from AbstractOrchestrator
✓ All async
✓ Type hints
```

**Verification:**
```bash
python -c "from backend.orchestrator.phase3 import Phase3Orchestrator; print('✓ OK')"
mypy backend/orchestrator/
```

**Commit: `git commit -m "feat: add Phase 3 Content orchestrator"`**

---

### PROMPT 20: Create Phase 4 Vulnerability Scanner Orchestrator

**File to Create:** `backend/orchestrator/phase4.py`

```
[TASK]
Create Phase4Orchestrator - vulnerability scanning

class Phase4Orchestrator(AbstractOrchestrator):
    """Phase 4: Vulnerability Scanning."""
    
    async def execute(self) -> Dict[str, Any]:
        """Execute vulnerability scanning."""
        await self.start()
        
        try:
            subdomains = await self._get_subdomains()
            
            for subdomain in subdomains:
                # Run Nmap scan
                open_ports = await self._run_nmap(subdomain)
                
                # Run web vulnerability scanning
                web_vulns = await self._run_web_scanner(subdomain)
                
                # Check for known vulns
                known_vulns = await self._check_known_vulns(subdomain)
                
                # Check SSL/TLS
                ssl_issues = await self._check_ssl(subdomain)
            
            await self._save_vulnerabilities()
            await self._calculate_risk_scores()
            await self.finish()
            return self.results
        
        except Exception as e:
            self.update_status("failed")
            raise
    
    async def _run_nmap(self, subdomain: str) -> List[Dict]:
        """Run Nmap port scan."""
        return []
    
    async def _run_web_scanner(self, subdomain: str) -> List[Dict]:
        """Run web vulnerability scanner."""
        return []
    
    async def _check_known_vulns(self, subdomain: str) -> List[Dict]:
        """Check for known vulnerabilities."""
        return []
    
    async def _check_ssl(self, subdomain: str) -> List[Dict]:
        """Check SSL/TLS configuration."""
        return []
    
    async def _save_vulnerabilities(self) -> None:
        """Save vulnerabilities to database."""
        pass
    
    async def _calculate_risk_scores(self) -> None:
        """Calculate overall risk scores."""
        pass

REQUIREMENTS:
✓ Same pattern
✓ Calculates risk at end
✓ Saves all findings
```

**Verification:**
```bash
python -c "from backend.orchestrator.phase4 import Phase4Orchestrator; print('✓ OK')"
mypy backend/orchestrator/
```

**Commit: `git commit -m "feat: add Phase 4 Vulnerability orchestrator"`**

---

### PROMPT 21: Create Main Orchestrator Coordinator

**File to Create:** `backend/orchestrator/coordinator.py`

```
[TASK]
Create main coordinator that runs all 4 phases sequentially

class ScanCoordinator:
    """Coordinates all phases of scanning."""
    
    def __init__(self, scan_run_id: int):
        self.scan_run_id = scan_run_id
        self.phases = []
        self.overall_results = {}
    
    async def run_full_scan(self) -> Dict[str, Any]:
        """Run complete scan from Phase 1 to Phase 4."""
        try:
            # Phase 1: Discovery
            phase1 = Phase1Orchestrator(self.scan_run_id)
            results1 = await phase1.execute()
            self.overall_results["phase1"] = results1
            
            # Phase 2: Intelligence
            phase2 = Phase2Orchestrator(self.scan_run_id)
            results2 = await phase2.execute()
            self.overall_results["phase2"] = results2
            
            # Phase 3: Content
            phase3 = Phase3Orchestrator(self.scan_run_id)
            results3 = await phase3.execute()
            self.overall_results["phase3"] = results3
            
            # Phase 4: Vulnerabilities
            phase4 = Phase4Orchestrator(self.scan_run_id)
            results4 = await phase4.execute()
            self.overall_results["phase4"] = results4
            
            # Update ScanRun status to completed
            await self._mark_scan_complete()
            
            return self.overall_results
        
        except Exception as e:
            await self._mark_scan_failed(str(e))
            raise
    
    async def _mark_scan_complete(self) -> None:
        """Mark scan as completed in database."""
        pass
    
    async def _mark_scan_failed(self, error: str) -> None:
        """Mark scan as failed in database."""
        pass

REQUIREMENTS:
✓ Runs all phases sequentially
✓ Proper error handling
✓ Updates database status
✓ Returns combined results
```

**Verification:**
```bash
python -c "from backend.orchestrator.coordinator import ScanCoordinator; print('✓ OK')"
mypy backend/orchestrator/
```

**Commit: `git commit -m "feat: add ScanCoordinator for sequential phase execution"`**

---

### PROMPT 22: Create Tests for Orchestrator

**File to Create:** `backend/tests/test_orchestrator.py`

```
[TASK]
Create tests for orchestrator modules

TESTS:

1. test_abstract_orchestrator_cannot_instantiate()
   - Try to create AbstractOrchestrator directly
   - Should raise error (it's abstract)

2. test_phase1_orchestrator_init()
   - Create Phase1Orchestrator
   - Check attributes initialized

3. test_phase1_orchestrator_status_update()
   - Create orchestrator
   - Call update_status()
   - Verify status changed

4. test_phase1_record_result()
   - Record result
   - Verify result stored

5. test_phase1_get_duration()
   - Start and finish orchestrator
   - Get duration
   - Verify duration is reasonable

6. test_all_phases_executable()
   - Create all phase orchestrators
   - Call validate_inputs()
   - Should return True

7. test_coordinator_initialization()
   - Create ScanCoordinator
   - Check initialization

8. test_coordinator_phases_sequence()
   - Create coordinator
   - Verify phases can be run in order

SUCCESS CRITERIA:
✓ 8+ tests
✓ All tests pass
✓ >85% coverage

VERIFICATION:
pytest backend/tests/test_orchestrator.py -v
pytest backend/tests/ --cov=backend
```

**Commit: `git commit -m "feat: add orchestrator unit tests (85%+ coverage)"`**

---

## Summary: Week 5-6 Deliverables

- ✅ Abstract orchestrator base class
- ✅ 4 phase orchestrators (Discovery, Intelligence, Content, Vulns)
- ✅ Main coordinator for sequential execution
- ✅ Comprehensive tests
- ✅ 85%+ coverage
- ✅ All models properly typed and documented

---

## 🧠 WEEK 7-10: Intelligence Modules
### Build Foundation for Smart Analysis

---

### PROMPT 23: Create Risk Scoring Module

**File to Create:** `backend/intelligence/risk_scorer.py`

```
[TASK]
Create risk scoring engine

class RiskScorer:
    """Calculate risk scores based on vulnerabilities."""
    
    # Weight definitions
    CRITICAL_WEIGHT = 10
    HIGH_WEIGHT = 5
    MEDIUM_WEIGHT = 2
    LOW_WEIGHT = 1
    
    @staticmethod
    def calculate_score(vulnerabilities: List[Vulnerability]) -> int:
        """Calculate overall risk score (0-100)."""
        if not vulnerabilities:
            return 0
        
        critical = sum(1 for v in vulnerabilities if v.severity >= 90)
        high = sum(1 for v in vulnerabilities if 70 <= v.severity < 90)
        medium = sum(1 for v in vulnerabilities if 40 <= v.severity < 70)
        low = sum(1 for v in vulnerabilities if v.severity < 40)
        
        total = (
            critical * RiskScorer.CRITICAL_WEIGHT +
            high * RiskScorer.HIGH_WEIGHT +
            medium * RiskScorer.MEDIUM_WEIGHT +
            low * RiskScorer.LOW_WEIGHT
        )
        
        # Normalize to 0-100
        max_possible = len(vulnerabilities) * RiskScorer.CRITICAL_WEIGHT
        if max_possible == 0:
            return 0
        
        score = int((total / max_possible) * 100)
        return min(100, max(0, score))
    
    @staticmethod
    def get_risk_level(score: int) -> str:
        """Get risk level from score."""
        if score >= 80:
            return "CRITICAL"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "INFO"

REQUIREMENTS:
✓ Static methods for scoring
✓ Type hints
✓ Docstrings
✓ Test coverage

TESTS:
- test_calculate_score_empty()
- test_calculate_score_critical()
- test_calculate_score_mixed()
- test_get_risk_level()

VERIFICATION:
pytest backend/tests/test_risk_scorer.py -v
```

**Commit: `git commit -m "feat: add risk scoring intelligence module"`**

---

### PROMPT 24: Create Threat Intelligence Module

**File to Create:** `backend/intelligence/threat_intel.py`

```
[TASK]
Create threat intel module - checks against external threat databases

class ThreatIntelligence:
    """Check domains/IPs against threat intel sources."""
    
    def __init__(self):
        # Initialize threat intel APIs
        self.abuseipdb_api = os.getenv("ABUSEIPDB_API_KEY")
        self.virustotal_api = os.getenv("VIRUSTOTAL_API_KEY")
    
    async def check_ip_reputation(self, ip_address: str) -> Dict[str, Any]:
        """Check IP address reputation."""
        # Call AbuseIPDB API
        # Return threat status
        return {"reputation": "clean", "abuse_score": 0}
    
    async def check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation."""
        # Call VirusTotal API
        # Return threat status
        return {"reputation": "clean", "detections": 0}
    
    async def check_indicators(self, indicators: List[str]) -> Dict[str, Any]:
        """Check multiple indicators."""
        results = {}
        for indicator in indicators:
            # Determine type (IP or domain)
            # Check appropriate API
            pass
        return results

TESTS:
- test_check_ip_reputation()
- test_check_domain_reputation()
- test_check_indicators()

VERIFICATION:
pytest backend/tests/test_threat_intel.py -v
```

**Commit: `git commit -m "feat: add threat intelligence integration module"`**

---

### PROMPT 25: Create Compliance Checker Module

**File to Create:** `backend/intelligence/compliance_checker.py`

```
[TASK]
Create compliance checking module

class ComplianceChecker:
    """Check for compliance violations."""
    
    def __init__(self, report_type: str):
        self.report_type = report_type  # pci-dss, hipaa, gdpr, iso27001
        self.findings = []
    
    def check_pci_dss(self, scan_data: Dict) -> List[Dict]:
        """Check PCI-DSS compliance."""
        findings = []
        
        # Check for HTTPS
        if not scan_data.get("https_enabled"):
            findings.append({
                "requirement_id": "PCI-DSS-4.1",
                "status": "failed",
                "finding": "HTTPS not enabled"
            })
        
        # Check for weak ciphers
        if scan_data.get("weak_ciphers"):
            findings.append({
                "requirement_id": "PCI-DSS-6.5.10",
                "status": "failed",
                "finding": "Weak ciphers detected"
            })
        
        return findings
    
    def check_hipaa(self, scan_data: Dict) -> List[Dict]:
        """Check HIPAA compliance."""
        # Similar to PCI-DSS but different rules
        return []
    
    def check_gdpr(self, scan_data: Dict) -> List[Dict]:
        """Check GDPR compliance."""
        # Check for data exposure, security measures
        return []

TESTS:
- test_check_pci_dss()
- test_check_hipaa()
- test_check_gdpr()

VERIFICATION:
pytest backend/tests/test_compliance_checker.py -v
```

**Commit: `git commit -m "feat: add compliance checking module (PCI-DSS, HIPAA, GDPR)"`**

---

### PROMPT 26-28: Create Additional Intelligence Modules (3 prompts)

Continue creating:
- Change Detection Module
- Dependency Mapping Module  
- Configuration Analysis Module

Each follows same pattern as 23-25.

**Quick version:**

```
# PROMPT 26
File: backend/intelligence/change_detector.py
Class: ChangeDetector
Methods: detect_new_vulns(), detect_new_assets(), detect_removed_services()

# PROMPT 27
File: backend/intelligence/dependency_mapper.py
Class: DependencyMapper
Methods: map_dependencies(), find_critical_dependencies(), detect_supply_chain_risks()

# PROMPT 28
File: backend/intelligence/config_analyzer.py
Class: ConfigurationAnalyzer
Methods: analyze_ssl_config(), analyze_headers(), detect_misconfigurations()
```

Each with tests, type hints, docstrings.

**Commits:**
```
git commit -m "feat: add change detection intelligence module"
git commit -m "feat: add dependency mapping intelligence module"
git commit -m "feat: add configuration analysis intelligence module"
```

---

## 🌐 WEEK 11-12: API Server
### Build FastAPI REST Interface

---

### PROMPT 29: Create Main FastAPI Application

**File to Create:** `backend/main.py`

```
[TASK]
Create FastAPI application with middleware

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

app = FastAPI(
    title="ReconX Enterprise",
    description="Professional vulnerability scanning platform",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize on startup."""
    logger.info("ReconX Enterprise API starting...")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("ReconX Enterprise API shutting down...")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Routes will be imported here
from backend.api import routes

TESTS:
- test_health_check()
- test_startup_event()

VERIFICATION:
python -c "from backend.main import app; print('✓ App created')"
```

**Commit: `git commit -m "feat: create FastAPI main application with middleware"`**

---

### PROMPT 30: Create Scan Routes

**File to Create:** `backend/api/routes/scans.py`

```
[TASK]
Create scan management endpoints

from fastapi import APIRouter, HTTPException, status
from backend.db.schemas import ScanRunCreate, ScanRunResponse
from backend.db.models import ScanRun
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/scans", tags=["scans"])

@router.post("/", response_model=Dict[str, Any], status_code=201)
async def create_scan(request: ScanRunCreate, db: Session):
    """Create a new scan.
    
    Args:
        request: Scan parameters
        db: Database session
    
    Returns:
        Scan created response with scan_id
    """
    if not request.domain:
        raise HTTPException(400, "Domain required")
    
    scan = ScanRun(
        domain=request.domain,
        scan_type=request.scan_type
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    return {"scan_id": scan.id, "status": "pending"}

@router.get("/{scan_id}", response_model=ScanRunResponse)
async def get_scan(scan_id: int, db: Session):
    """Get scan by ID."""
    scan = db.query(ScanRun).filter(ScanRun.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    return scan

@router.get("/", response_model=List[ScanRunResponse])
async def list_scans(db: Session):
    """List all scans."""
    scans = db.query(ScanRun).all()
    return scans

@router.post("/{scan_id}/start")
async def start_scan(scan_id: int, db: Session):
    """Start a scan execution."""
    scan = db.query(ScanRun).filter(ScanRun.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    
    # Trigger orchestrator
    scan.status = "running"
    db.commit()
    
    return {"scan_id": scan.id, "status": "running"}

REQUIREMENTS:
✓ 4+ endpoints
✓ Type hints
✓ Proper error handling
✓ Validation

TESTS:
- test_create_scan()
- test_get_scan_404()
- test_list_scans()
- test_start_scan()

VERIFICATION:
pytest backend/tests/test_api_scans.py -v
```

**Commit: `git commit -m "feat: add scan management API endpoints"`**

---

### PROMPT 31: Create Vulnerabilities Routes

**File to Create:** `backend/api/routes/vulnerabilities.py`

```
[TASK]
Create vulnerability reporting endpoints

@router.get("/{vuln_id}", response_model=VulnerabilityResponse)
async def get_vulnerability(vuln_id: int, db: Session):
    """Get vulnerability details."""
    vuln = db.query(Vulnerability).filter(Vulnerability.id == vuln_id).first()
    if not vuln:
        raise HTTPException(404, "Vulnerability not found")
    return vuln

@router.get("/scan/{scan_id}")
async def get_scan_vulnerabilities(scan_id: int, db: Session):
    """Get all vulnerabilities for a scan."""
    vulns = db.query(Vulnerability).filter(
        Vulnerability.scan_run_id == scan_id
    ).order_by(Vulnerability.severity.desc()).all()
    return vulns

@router.get("/scan/{scan_id}/summary")
async def get_vulnerability_summary(scan_id: int, db: Session):
    """Get vulnerability summary for scan."""
    vulns = db.query(Vulnerability).filter(
        Vulnerability.scan_run_id == scan_id
    ).all()
    
    critical = sum(1 for v in vulns if v.severity >= 90)
    high = sum(1 for v in vulns if 70 <= v.severity < 90)
    medium = sum(1 for v in vulns if 40 <= v.severity < 70)
    low = sum(1 for v in vulns if v.severity < 40)
    
    return {
        "total": len(vulns),
        "critical": critical,
        "high": high,
        "medium": medium,
        "low": low
    }

TESTS:
- test_get_vulnerability()
- test_get_scan_vulnerabilities()
- test_get_vulnerability_summary()
```

**Commit: `git commit -m "feat: add vulnerability reporting API endpoints"`**

---

### PROMPT 32: Create Reports Routes

**File to Create:** `backend/api/routes/reports.py`

```
[TASK]
Create report generation endpoints

@router.post("/{scan_id}/report")
async def generate_report(
    scan_id: int,
    report_type: str = "executive",  # executive, detailed, compliance
    db: Session = None
):
    """Generate report for scan."""
    scan = db.query(ScanRun).filter(ScanRun.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    
    # Generate based on type
    if report_type == "executive":
        report = await generate_executive_report(scan)
    elif report_type == "detailed":
        report = await generate_detailed_report(scan)
    elif report_type == "compliance":
        report = await generate_compliance_report(scan)
    else:
        raise HTTPException(400, "Invalid report type")
    
    return report

@router.get("/{scan_id}/report/{report_id}")
async def get_report(scan_id: int, report_id: int, db: Session):
    """Get saved report."""
    report = db.query(SavedReport).filter(
        SavedReport.id == report_id,
        SavedReport.scan_run_id == scan_id
    ).first()
    if not report:
        raise HTTPException(404, "Report not found")
    return report

TESTS:
- test_generate_executive_report()
- test_generate_detailed_report()
- test_get_report_404()
```

**Commit: `git commit -m "feat: add report generation API endpoints"`**

---

### PROMPT 33-35: Create Additional API Routes (3 prompts)

Create authentication, assets, and compliance routes:

**PROMPT 33:**
File: `backend/api/routes/auth.py`
Endpoints: POST /auth/login, POST /auth/token, POST /auth/refresh

**PROMPT 34:**
File: `backend/api/routes/assets.py`
Endpoints: GET /assets, GET /assets/{asset_id}, GET /assets/domain/{domain}

**PROMPT 35:**
File: `backend/api/routes/compliance.py`
Endpoints: POST /compliance/check, GET /compliance/{report_id}, GET /compliance/status

Each with full implementation and tests.

**Commits:**
```
git commit -m "feat: add authentication API endpoints"
git commit -m "feat: add asset management API endpoints"
git commit -m "feat: add compliance checking API endpoints"
```

---

## 🎨 WEEK 13-14: Frontend UI
### Build React Web Interface

---

### PROMPT 36: Create React Setup and Dashboard

**File to Create:** `frontend/src/App.jsx`

```
[TASK]
Create main React application

import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import ScanList from './pages/ScanList'
import VulnerabilityDetail from './pages/VulnerabilityDetail'
import Reports from './pages/Reports'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <Navigation />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/scans" element={<ScanList />} />
            <Route path="/vulnerabilities/:id" element={<VulnerabilityDetail />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App

COMPONENTS TO CREATE:
- Navigation (header with menu)
- Dashboard (main overview page)
- ScanList (list all scans)
- VulnerabilityDetail (show vulnerability details)
- Reports (generate/view reports)

TESTS:
- test_app_renders()
- test_navigation()
- test_routing()
```

**Commit: `git commit -m "feat: create React application with routing"`**

---

### PROMPT 37: Create Dashboard Component

**File to Create:** `frontend/src/pages/Dashboard.jsx`

```
[TASK]
Create main dashboard showing key metrics

import React, { useState, useEffect } from 'react'
import { fetchDashboardData } from '../api/api'
import MetricCard from '../components/MetricCard'
import VulnerabilityChart from '../components/VulnerabilityChart'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    async function loadData() {
      try {
        const result = await fetchDashboardData()
        setData(result)
      } catch (error) {
        console.error(error)
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [])
  
  if (loading) return <div>Loading...</div>
  
  return (
    <div className="dashboard">
      <h1>ReconX Enterprise Dashboard</h1>
      
      <div className="metrics">
        <MetricCard title="Total Scans" value={data.total_scans} />
        <MetricCard title="Critical Vulns" value={data.critical} />
        <MetricCard title="High Vulns" value={data.high} />
        <MetricCard title="Assets Monitored" value={data.assets} />
      </div>
      
      <VulnerabilityChart data={data.chart_data} />
    </div>
  )
}

COMPONENTS NEEDED:
- MetricCard
- VulnerabilityChart

FEATURES:
- Fetch data from API
- Display key metrics
- Show charts
- Responsive design
```

**Commit: `git commit -m "feat: create dashboard with metrics and charts"`**

---

### PROMPT 38-40: Create Additional UI Pages (3 prompts)

Create remaining pages for complete UI:

**PROMPT 38:**
File: `frontend/src/pages/ScanList.jsx`
Features: List scans, filter, sort, create new scan

**PROMPT 39:**
File: `frontend/src/components/VulnerabilityCard.jsx`
Features: Display vulnerability details, severity badge, status

**PROMPT 40:**
File: `frontend/src/pages/Reports.jsx`
Features: Generate reports, download as PDF/CSV, view saved reports

**Commits:**
```
git commit -m "feat: add scan list page with filters"
git commit -m "feat: add vulnerability detail card component"
git commit -m "feat: add report generation and download"
```

---

## ✅ WEEK 15-16: Testing & Deployment
### Finalize and Deploy

---

### PROMPT 41: Create Comprehensive Integration Tests

**File to Create:** `backend/tests/test_full_workflow.py`

```
[TASK]
Create end-to-end workflow tests

async def test_complete_scan_workflow():
    """Test complete scan from creation to reporting."""
    
    # 1. Create scan
    scan = await create_scan("example.com")
    assert scan.id
    
    # 2. Run discovery phase
    phase1 = Phase1Orchestrator(scan.id)
    result1 = await phase1.execute()
    assert result1["passive_subdomains"] > 0
    
    # 3. Run intelligence phase
    phase2 = Phase2Orchestrator(scan.id)
    result2 = await phase2.execute()
    assert result2["technologies_found"] >= 0
    
    # 4. Run content phase
    phase3 = Phase3Orchestrator(scan.id)
    result3 = await phase3.execute()
    
    # 5. Run vulnerability phase
    phase4 = Phase4Orchestrator(scan.id)
    result4 = await phase4.execute()
    
    # 6. Generate report
    report = await generate_report(scan.id, "detailed")
    assert report["vulnerabilities"] is not None
    
    # 7. Verify database state
    scan = db.query(ScanRun).filter(ScanRun.id == scan.id).first()
    assert scan.status == "completed"

ADDITIONAL TESTS:
- test_api_endpoints()
- test_database_constraints()
- test_error_handling()

VERIFICATION:
pytest backend/tests/test_full_workflow.py -v

Run all tests:
pytest backend/tests/ -v --cov=backend --cov-report=html

Check: >90% coverage
```

**Commit: `git commit -m "feat: add end-to-end integration tests"`**

---

### PROMPT 42: Create Docker Image Build

**File to Create:** `Dockerfile`

```
[TASK]
Create production Docker image

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY backend/ ./backend/
COPY scanner/ ./scanner/

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

REQUIREMENTS:
✓ Multi-stage build optional
✓ Production ready
✓ Health checks included
```

**Commit: `git commit -m "feat: add production Dockerfile for API server"`**

---

### PROMPT 43: Update Docker Compose for Production

**File to Update:** `docker-compose.prod.yml`

```
[TASK]
Create production docker-compose file

version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/reconx
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
  
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: reconx
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pg_data:/var/lib/postgresql/data
    restart: unless-stopped
  
  redis:
    image: redis:7-alpine
    restart: unless-stopped
  
  worker:
    build: .
    command: celery -A backend.celery_app worker -l info
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

volumes:
  pg_data:

TESTS:
- docker-compose -f docker-compose.prod.yml up -d
- curl http://localhost:8000/health
- Verify all services running
```

**Commit: `git commit -m "feat: add production docker-compose configuration"`**

---

### PROMPT 44: Create Kubernetes Manifests for Deployment

**File to Create:** `deployment/k8s/deployment.yaml`

```
[TASK]
Create Kubernetes deployment manifest

apiVersion: apps/v1
kind: Deployment
metadata:
  name: reconx-api
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: reconx-api
  template:
    metadata:
      labels:
        app: reconx-api
    spec:
      containers:
      - name: api
        image: reconx:v2.0.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: reconx-secrets
              key: database_url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: reconx-secrets
              key: redis_url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: reconx-api
spec:
  type: LoadBalancer
  selector:
    app: reconx-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000

REQUIREMENTS:
✓ 3 replicas
✓ Health checks
✓ Secrets management
✓ Service exposed
```

**Commit: `git commit -m "feat: add Kubernetes deployment manifests"`**

---

### PROMPT 45: Create Deployment Documentation

**File to Create:** `docs/DEPLOYMENT.md`

```
# Deployment Guide

## Local Development

```bash
docker-compose up -d
pytest backend/tests/
make test
```

## Production Deployment (Docker Compose)

```bash
docker-compose -f docker-compose.prod.yml up -d
curl http://localhost:8000/health
```

## Kubernetes Deployment

```bash
kubectl apply -f deployment/k8s/secrets.yaml
kubectl apply -f deployment/k8s/deployment.yaml
kubectl apply -f deployment/k8s/service.yaml

# Verify
kubectl get pods
kubectl logs <pod-name>
```

## Database Migration

```bash
alembic upgrade head
```

## Monitoring

- API health: http://localhost:8000/health
- Logs: docker-compose logs -f
- Database: pgAdmin (localhost:5050)
```

**Commit: `git commit -m "feat: add deployment documentation"`**

---

### PROMPT 46: Create Final Coverage Report and Summary

```
[TASK]
Generate final test coverage report

Run:
pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term

Verify:
- ✓ >90% coverage overall
- ✓ >85% coverage per module
- ✓ All critical paths tested
- ✓ All edge cases covered

Generate summary:
- Total lines: ~15,000
- Total tests: 100+
- Coverage: >90%
- All tests passing: YES
```

**Commit: `git commit -m "test: achieve 90%+ test coverage for production release"`**

---

### PROMPT 47: Create Final Documentation

**File to Create:** `docs/COMPLETE_GUIDE.md`

```
# ReconX Enterprise v2.0 - Complete Implementation Guide

## Project Overview
- 25 database models
- 4-phase orchestrator
- 6 intelligence modules
- 15+ API endpoints
- React frontend
- Kubernetes-ready deployment

## Architecture
[Describe the complete architecture]

## Getting Started
[Quick start guide]

## Development
[Development backend]

## Deployment
[Production deployment]

## API Documentation
[All endpoints]

## Troubleshooting
[Common issues and solutions]
```

**Commit: `git commit -m "docs: add complete implementation documentation"`**

---

### PROMPT 48: Final Verification and Sign-Off

```
[TASK]
Final verification before production release

CHECKLIST:

Database Layer:
- [ ] 25 models created ✓
- [ ] All typed and documented ✓
- [ ] 90%+ tests coverage ✓
- [ ] Migrations working ✓

Backend Logic:
- [ ] 4-phase orchestrator working ✓
- [ ] 6 intelligence modules created ✓
- [ ] All async/concurrent ✓
- [ ] 90%+ test coverage ✓

API:
- [ ] 15+ endpoints created ✓
- [ ] Authentication working ✓
- [ ] Error handling functional ✓
- [ ] Rate limiting in place ✓

Frontend:
- [ ] React UI complete ✓
- [ ] Dashboard functional ✓
- [ ] Report generation working ✓

Deployment:
- [ ] Docker image builds ✓
- [ ] Docker Compose works ✓
- [ ] Kubernetes manifests ready ✓
- [ ] CI/CD pipeline functional ✓

Testing:
- [ ] Unit tests: >90% coverage ✓
- [ ] Integration tests passing ✓
- [ ] E2E tests functional ✓
- [ ] All vulnerabilities addressed ✓

Documentation:
- [ ] API docs complete ✓
- [ ] Deployment guide done ✓
- [ ] User guide written ✓
- [ ] Architecture documented ✓

FINAL COMMIT:
git commit -m "release: ReconX Enterprise v2.0 production ready"
git tag -a v2.0.0 -m "Production release v2.0.0"
git push origin --all --tags
```

**Status: ✅ PRODUCTION READY**

---

## 📊 Final Summary

### What Was Built (Week 3-16)

| Component | Count | Coverage | Status |
|-----------|-------|----------|--------|
| Database Models | 25 | 90%+ | ✅ |
| API Endpoints | 15+ | 90%+ | ✅ |
| Tests | 100+ | 90%+ | ✅ |
| Intelligence Modules | 6 | 90%+ | ✅ |
| React Components | 10+ | N/A | ✅ |
| Total Code Lines | ~15,000 | Full | ✅ |

### Follow This Execution Path

1. Read this entire file once (30-45 min)
2. Start with PROMPT 1
3. Copy entire prompt (including context)
4. Paste into Cursor IDE (Cmd+K)
5. Accept generated code
6. Run verification commands
7. Commit (atomic, semantic message)
8. Next prompt
9. By Friday: Complete week
10. Repeat for each week

### Success Formula

```
Quality = Type Hints + Tests + Documentation + Code Review
Speed = Atomic Tasks + Reusable Patterns + Clear Context
Professional = Quality + Speed + Consistency + Error Handling

ReconX Enterprise = All of the above
```

---

**You now have EVERY prompt needed to build the complete system sequentially with a single agent.**

**Start with PROMPT 1 and execute sequentially through PROMPT 48.**

**Expected completion: 16 weeks**

**Good luck! 🚀**
