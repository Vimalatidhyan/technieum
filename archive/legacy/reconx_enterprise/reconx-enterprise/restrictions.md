# 🔒 Claude Code Agent - Restrictions & Constraints

**Purpose:** Hard constraints Claude MUST follow when generating code for ReconX Enterprise

**Version:** v2.0  
**Last Updated:** February 2026  
**Scope:** All generated code must comply with these restrictions

---

## 🚫 HARD CONSTRAINTS (Non-Negotiable)

### 1. TYPE HINTS - 100% Coverage Required

**RULE:** Every function, method, parameter, and return value must have explicit type hints.

```python
❌ WRONG - No type hints:
def calculate_risk(vulnerability):
    return vulnerability['score'] * 2

✅ CORRECT - Full type hints:
def calculate_risk(vulnerability: dict[str, Any]) -> float:
    """Calculate risk score for vulnerability.
    
    Args:
        vulnerability: Vulnerability data dictionary
        
    Returns:
        Risk score as float between 0-100
    """
    return vulnerability['score'] * 2
```

**EXCEPTIONS:** Only when documenting in docstring:
```python
# Exception example for complex types:
from typing import Any

def process_data(data: Any) -> dict[str, Any]:  # Any justified below
    """Process arbitrary data.
    
    Note: 'Any' used for flexibility with external API responses 
    that have variable schema. Better approach: define Pydantic model.
    """
```

**Class variables:**
```python
❌ WRONG:
class ScanRun:
    id = None
    domain = None

✅ CORRECT:
class ScanRun:
    id: int
    domain: str
    status: ScanStatus = ScanStatus.PENDING
```

**Function variables when unclear:**
```python
❌ WRONG:
result = perform_scan()

✅ CORRECT:
result: ScanResult = perform_scan()
```

---

### 2. DOCSTRINGS - Google Style Required

**RULE:** ALL classes and functions must have comprehensive docstrings using Google style format.

**Class docstring template:**
```python
✅ CORRECT:
class RiskScoringEngine:
    """Calculates risk scores for vulnerabilities using CVSS v3.1 scoring.
    
    This engine normalizes CVSS scores, applies custom weighting for 
    organizational context, and factors in threat intelligence data to
    produce a final risk score between 0-100.
    
    Attributes:
        weights: Dictionary of weighting factors for different vulnerability types
        redis_client: Redis client for caching computed scores
        logger: Structured logger instance
        
    Example:
        >>> engine = RiskScoringEngine()
        >>> score = engine.calculate_risk(vulnerability_data)
        >>> print(f"Risk score: {score}")
    """
```

**Function docstring template:**
```python
✅ CORRECT:
async def calculate_risk(
    self,
    vulnerability: VulnerabilityData,
    context: dict[str, Any] | None = None
) -> float:
    """Calculate risk score for a single vulnerability.
    
    Normalizes CVSS v3.1 score, applies organizational weighting factors,
    and incorporates threat intelligence data to produce final risk score.
    
    Args:
        vulnerability: Vulnerability data including CVSS v3.1 vector
        context: Optional organizational context (industry, criticality)
        
    Returns:
        Risk score as float between 0-100
        
    Raises:
        ValueError: If CVSS vector is invalid
        RedisCacheError: If cache operation fails
        
    Example:
        >>> vuln_data = VulnerabilityData(cvss_score=7.5, vector="...")
        >>> score = engine.calculate_risk(vuln_data)
        >>> assert 0 <= score <= 100
    """
```

**Property docstring:**
```python
✅ CORRECT:
@property
def is_cached(self) -> bool:
    """Check if engine results are cached in Redis.
    
    Returns:
        True if cache backend is available and healthy
    """
```

**Section Comments in Long Methods:**
```python
✅ CORRECT:
async def complex_operation(self) -> Result:
    """Perform complex multi-step operation.
    
    [Full docstring...]
    """
    # Step 1: Validate inputs
    self._validate_inputs()
    
    # Step 2: Fetch from cache if available
    cached = await self.redis_client.get(cache_key)
    
    # Step 3: Calculate if not cached
    if not cached:
        result = self._calculate()
```

---

### 3. TEST COVERAGE - 90% Minimum

**RULE:** All code must have 90%+ test coverage measured by pytest-cov.

**Coverage requirements by module:**
- `backend/db/models.py` → 95% (models are critical)
- `backend/orchestrator/*.py` → 90% (core business logic)
- `backend/intelligence/*.py` → 90% (intelligence engines)
- `backend/api/routes/*.py` → 90% (API endpoints)
- `backend/api/auth.py` → 85% (some external auth harder to test)
- `backend/utils/*.py` → 80% (utilities can have lower coverage)

**Test file structure:**
```python
✅ CORRECT:
# backend/tests/test_models.py
import pytest
from sqlalchemy import create_engine
from backend.db.models import ScanRun, ScanStatus

class TestScanRun:
    """Test suite for ScanRun model."""
    
    @pytest.fixture
    def db_session(self):
        """Create test database session."""
        engine = create_engine("sqlite:///:memory:")
        # ... teardown
        
    def test_scan_run_creation(self, db_session):
        """Test ScanRun model instantiation."""
        scan = ScanRun(domain="example.com", status=ScanStatus.PENDING)
        assert scan.domain == "example.com"
        
    def test_scan_run_relationships(self, db_session):
        """Test ScanRun relationships with Subdomain."""
        # Test with multiple edge cases
        
    @pytest.mark.parametrize("status", [ScanStatus.PENDING, ScanStatus.RUNNING])
    def test_scan_run_status_transitions(self, db_session, status):
        """Test status transition logic."""
        # Test each status
```

**Verification command:**
```bash
pytest backend/ --cov=backend --cov-report=html --cov-fail-under=90
# Must pass with 0 failures and coverage >= 90%
```

---

### 4. CODE QUALITY - Black, Flake8, Isort, Mypy

**RULE:** All code must pass quality gates without modifications.

**Mypy - Type Checking:**
```bash
mypy backend/ --strict

# Strict mode enforces:
# ✅ All functions have return type annotations
# ✅ All parameters have type annotations
# ✅ No implicit Optional (use Optional[T] explicitly)
# ✅ No Any without comment explaining why
# ✅ All imports properly typed
```

**Black - Code Formatting:**
```bash
black backend/

# Rules:
# ✅ 88 character line length (Black's default)
# ✅ Double quotes for strings (except docstrings)
# ✅ Consistent spacing around operators
```

**Flake8 - Style Enforcement:**
```bash
flake8 backend/

# Config in .flake8:
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,docs,*.egg-info

# Common violations to avoid:
# ✅ F401: unused imports → remove or prefix with _
# ✅ E302: expected 2 blank lines → add blank lines
# ✅ W291: trailing whitespace → remove
```

**Isort - Import Organization:**
```bash
isort backend/

# Enforces ordering:
# 1. Standard library imports
# 2. Third-party imports
# 3. Local application imports
# Separated by blank lines, alphabetically sorted within groups

✅ CORRECT:
import asyncio
import json
from typing import Any

import sqlalchemy as sa
from fastapi import FastAPI

from backend.db.models import ScanRun
from backend.utils import logger
```

**All at Once:**
```bash
# Makefile target - use this to validate:
make quality

# Which runs:
mypy backend/ --strict
black backend/ --check  # (doesn't modify, just checks)
flake8 backend/
isort backend/ --check-only
```

---

### 5. ASYNC/AWAIT for I/O Operations

**RULE:** All database, API, and file I/O must use async/await.

```python
❌ WRONG - Blocking I/O:
def fetch_vulnerabilities(scan_id: int) -> list[Vulnerability]:
    vulnerabilities = session.query(Vulnerability).filter(...).all()
    return vulnerabilities

✅ CORRECT - Async I/O:
async def fetch_vulnerabilities(
    scan_id: int,
    session: AsyncSession
) -> list[Vulnerability]:
    """Fetch vulnerabilities for scan (async)."""
    result = await session.execute(
        select(Vulnerability).where(Vulnerability.scan_id == scan_id)
    )
    return result.scalars().all()
```

**API Calls:**
```python
❌ WRONG:
import requests
response = requests.get("https://api.virustotal.com/...")

✅ CORRECT:
import aiohttp
async with aiohttp.ClientSession() as session:
    async with session.get("https://api.virustotal.com/...") as resp:
        data = await resp.json()
```

**FastAPI Routes:**
```python
❌ WRONG:
@router.get("/scans/{scan_id}")
def get_scan(scan_id: int):
    scan = session.query(ScanRun).get(scan_id)
    return ScanResponse.from_orm(scan)

✅ CORRECT:
@router.get("/scans/{scan_id}")
async def get_scan(
    scan_id: int,
    session: AsyncSession = Depends(get_session)
) -> ScanResponse:
    result = await session.execute(
        select(ScanRun).where(ScanRun.id == scan_id)
    )
    scan = result.scalar_one_or_none()
    if not scan:
        raise HTTPException(status_code=404)
    return ScanResponse.from_orm(scan)
```

---

### 6. NO HARDCODED VALUES

**RULE:** All configuration must come from environment variables or config files.

```python
❌ WRONG - Hardcoded:
DATABASE_URL = "postgresql://user:pass@localhost/reconx"
LOG_LEVEL = "INFO"
API_KEY = "abc123secret"
MAX_RETRIES = 3

✅ CORRECT - From environment:
import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    api_key: str = os.getenv("API_KEY")  # Required, fail if not set
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    
    class Config:
        env_file = ".env"

settings = Settings()
```

**In code:**
```python
✅ CORRECT:
from backend.config import settings

logger.setLevel(settings.log_level)
MAX_RETRIES = settings.max_retries

@router.get("/endpoint")
async def endpoint():
    url = settings.external_api_url  # From config
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()
```

---

### 7. ERROR HANDLING & LOGGING

**RULE:** All errors must be logged, all external calls wrapped with try/except.

```python
❌ WRONG - No error handling:
def risky_operation():
    data = fetch_from_api()
    process(data)

✅ CORRECT - Full error handling:
import logging

logger = logging.getLogger(__name__)

async def safe_operation() -> dict[str, Any] | None:
    """Perform operation with error handling."""
    try:
        data = await fetch_from_api()
        return await process(data)
    except APITimeout as e:
        logger.warning(f"API timeout after {e.timeout}s, retrying...")
        return await safe_operation()  # Idempotent
    except APIError as e:
        logger.error(f"API error: {e.status_code} - {e.message}")
        raise  # Re-raise for caller to handle
    except Exception as e:
        logger.exception(f"Unexpected error in safe_operation: {e}")
        raise
```

**Custom exceptions:**
```python
# backend/utils/exceptions.py
class ReconXException(Exception):
    """Base exception for ReconX errors."""

class ScanException(ReconXException):
    """Raised when scan operation fails."""

class APIException(ReconXException):
    """Raised when external API call fails."""

class ComplianceException(ReconXException):
    """Raised when compliance check fails."""
```

---

### 8. SQLAlchemy Best Practices

**RULE:** Models must follow SQLAlchemy ORM best practices.

```python
❌ WRONG - Foreign keys without proper relationships:
class Subdomain(Base):
    __tablename__ = "subdomains"
    id: int = Column(Integer, primary_key=True)
    scan_id: int = Column(Integer)  # Missing ForeignKey
    scan_run = None  # Missing relationship

✅ CORRECT - Full relationship definition:
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

class Subdomain(Base):
    __tablename__ = "subdomains"
    id: int = Column(Integer, primary_key=True)
    scan_id: int = Column(Integer, ForeignKey("scan_runs.id"))
    scan_run: ScanRun = relationship(
        "ScanRun",
        back_populates="subdomains",
        lazy="select"  # Explicit lazy loading
    )
```

**Indexes on heavily queried columns:**
```python
✅ CORRECT:
class ScanRun(Base):
    __tablename__ = "scan_runs"
    id: int = Column(Integer, primary_key=True, index=True)
    domain: str = Column(String(255), nullable=False, index=True)  # Query by domain
    status: ScanStatus = Column(String(20), default=ScanStatus.PENDING, index=True)  # Filter by status
    created_at: datetime = Column(DateTime, default=datetime.utcnow, index=True)  # Time range queries
    
    __table_args__ = (
        Index("ix_scan_runs_domain_status", "domain", "status"),  # Composite index
    )
```

---

### 9. Pydantic Validation for APIs

**RULE:** All API request/response data must be validated with Pydantic models.

```python
❌ WRONG - No validation:
@router.post("/scans")
async def create_scan(data: dict):
    scan = ScanRun(**data)  # Unvalidated
    return scan

✅ CORRECT - Full validation:
from pydantic import BaseModel, Field, validator

class ScanCreateRequest(BaseModel):
    """Request to create new security scan."""
    domain: str = Field(..., min_length=1, max_length=255)
    scan_type: ScanType = Field(default=ScanType.FULL)
    priority: int = Field(ge=1, le=10, default=5)
    
    @validator('domain')
    def validate_domain(cls, v: str) -> str:
        """Validate domain is not empty and properly formatted."""
        if not v.strip():
            raise ValueError("Domain cannot be empty")
        return v.lower()

class ScanResponse(BaseModel):
    """Response with scan information."""
    id: int
    domain: str
    status: ScanStatus
    created_at: datetime
    
    class Config:
        from_attributes = True  # For ORM model conversion
```

---

### 10. Separation of Concerns

**RULE:** Each module has single responsibility. No mixing concerns.

**Module responsibilities:**
```
backend/db/         → Database models and schema only
backend/api/        → REST endpoints and request/response only
backend/orchestrator/ → Scan orchestration and sequencing only
backend/intelligence/ → Analysis and scoring algorithms
backend/tasks/      → Async job definitions (Celery)
backend/utils/      → Shared utilities and helpers
```

**No cross-module concerns:**
```python
❌ WRONG - API route doing database schema work:
@router.post("/scans")
async def create_scan(request: ScanCreateRequest):
    # This is orchestration logic, not API concern
    discovery_result = await run_discovery(request.domain)
    portscan_result = await run_portscan(discovery_result)
    # ...

✅ CORRECT - API delegates to orchestrator:
@router.post("/scans")
async def create_scan(
    request: ScanCreateRequest,
    session: AsyncSession = Depends(get_session)
) -> ScanResponse:
    """Create new scan and queue orchestration."""
    scan = ScanRun(domain=request.domain)
    session.add(scan)
    await session.commit()
    
    # Queue as async task
    await queue_scan_orchestration.delay(scan.id)
    
    return ScanResponse.from_orm(scan)
```

---

## ⚠️ STRONG CONSTRAINTS (Break only with justification)

### 1. No Global State
```python
❌ WRONG:
redis_client = redis.Redis()  # Global

def get_cache():
    return redis_client

✅ CORRECT:
from backend.config import get_redis_client

async def get_cache():
    client = await get_redis_client()
    return client
```

### 2. No Bare Exception Handlers
```python
❌ WRONG:
try:
    operation()
except:  # Too broad
    logger.error("Error")

✅ CORRECT:
try:
    operation()
except OperationError as e:
    logger.error(f"Operation failed: {e}")
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
```

### 3. No Mutable Default Arguments
```python
❌ WRONG:
def add_item(item: str, items: list = []):  # Mutable default
    items.append(item)
    return items

✅ CORRECT:
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### 4. No Raw SQL (use SQLAlchemy ORM)
```python
❌ WRONG:
vulnerabilities = session.execute(
    f"SELECT * FROM vulnerabilities WHERE severity='{severity}'"
).fetchall()

✅ CORRECT:
result = await session.execute(
    select(Vulnerability).where(Vulnerability.severity == severity)
)
vulnerabilities = result.scalars().all()
```

---

## 📋 CONSTRAINT CHECKLIST

Before asking Claude to generate code, verify:

- [ ] Type hints on all functions/params/returns
- [ ] Comprehensive docstrings (Google style)
- [ ] Test coverage 90%+ with pytest
- [ ] mypy --strict passes
- [ ] black format correct
- [ ] flake8 violations = 0
- [ ] isort properly ordered
- [ ] Async/await for all I/O
- [ ] No hardcoded configuration
- [ ] Error handling with logging
- [ ] SQLAlchemy relationships defined
- [ ] Pydantic validation for inputs
- [ ] Single responsibility per module
- [ ] No global state
- [ ] No bare exception handlers
- [ ] No mutable defaults
- [ ] SQLAlchemy queries (no raw SQL)

---

## 🔧 Configuration: How These Are Enforced

**pyproject.toml:**
```toml
[tool.black]
line-length = 88
target-version = ['py310']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.10"
strict = true
warn_unused_ignores = true

[tool.pytest.ini_options]
testpaths = ["backend/tests"]
addopts = "--cov=backend --cov-fail-under=90"
```

**.flake8:**
```
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,docs/*.egg-info
```

**Makefile:**
```makefile
quality:
	mypy backend/ --strict
	black backend/ --check
	flake8 backend/
	isort backend/ --check-only

test:
	pytest backend/ -v --cov=backend --cov-fail-under=90

fix:
	black backend/
	isort backend/
	autoflake --in-place --recursive backend/
```

---

## 🎯 Final Rule

**When Claude generates code, ALL constraints apply automatically. There are no exceptions.**

If a constraint seems impossible to meet, that's a signal the requirement needs refining. Ask clarifying questions or break the prompt into smaller pieces rather than violating constraints.

---

**Last updated:** February 2026  
**For questions:** See [claude.md](claude.md) or [error-recovery.md](error-recovery.md)
