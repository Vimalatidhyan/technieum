# ✅ Verification Checklist - Quality Gate Validation

**Purpose:** Comprehensive checklist to verify generated code meets all quality requirements

**Version:** v2.0  
**Scope:** Type hints, tests, coverage, code quality, documentation, integration

---

## 🎯 Quick Reference (30 seconds)

For each generated file:

```bash
# Step 1: Type checking
mypy <file> --strict

# Step 2: Formatting
black <file> --check

# Step 3: Linting
flake8 <file>

# Step 4: Imports
isort <file> --check-only

# Step 5: Tests
pytest backend/tests/test_<module>.py -v --cov=<module>

# All at once:
make quality && make test
```

If all pass → **Next prompt ✅**  
If any fail → [error-recovery.md](error-recovery.md)

---

## ✅ CHECKLIST 1: Code Quality

Use after saving generated code to file.

### 1.1 Type Hints (100% Required)

**Check:**
```bash
mypy <file> --strict --show-error-codes
```

**Expected:**
```
Success: no issues found in 1 source file
```

**Verification checklist:**
- [ ] Function parameters have type hints
- [ ] Function return types specified
- [ ] Class variables have type hints
- [ ] Generic types use brackets (list[str], dict[str, int])
- [ ] Optional types use Optional[T] (not T | None in older code)
- [ ] No Any without justification in docstring comment
- [ ] Complex types imported at top (from typing import Any, Optional, etc.)

**Example passing code:**
```python
def calculate_risk(
    vulnerability: VulnerabilityData,
    context: dict[str, Any] | None = None
) -> float:
    """Calculate risk score.
    
    Args:
        vulnerability: Vulnerability data
        context: Optional context dict (keys vary)
        
    Returns:
        Risk score 0-100
    """
    pass
```

### 1.2 Code Formatting (Black)

**Check:**
```bash
black <file> --check
```

**Expected:**
```
All done! ✨ 🍰 ✨
1 file would be left unchanged.
```

**Verification checklist:**
- [ ] Line length ≤ 88 characters
- [ ] Double quotes for strings (not single)
- [ ] Proper spacing around operators
- [ ] Two blank lines between top-level definitions
- [ ] One blank line between methods

**If fails:** Run `black <file>` to auto-fix

### 1.3 Linting (Flake8)

**Check:**
```bash
flake8 <file>
```

**Expected:**
```
[No output = no errors]
```

**Verification checklist:**
- [ ] No F401 (unused imports)
- [ ] No E302 (expected blank lines)
- [ ] No W291 (trailing whitespace)
- [ ] No E501 (line too long) - already caught by black
- [ ] No F821 (undefined names)
- [ ] No E704 (multiple statements on one line)

**Common violations and fixes:**

| Error | Fix |
|-------|-----|
| F401 unused import | Remove import or prefix with `_` |
| E302 expected 2 blank lines | Add blank lines between functions |
| W291 trailing whitespace | Remove spaces at line end |
| E999 syntax error | Fix Python syntax |
| F821 undefined name | Import the name or define it |

**If fails:** Check flake8 output, make manual fixes

### 1.4 Import Organization (Isort)

**Check:**
```bash
isort <file> --check-only --diff
```

**Expected:**
```
[No output = properly organized]
```

**Verification checklist:**
- [ ] Standard library imports first
- [ ] Third-party imports second
- [ ] Local imports third
- [ ] Blank line between groups
- [ ] Imports alphabetically sorted within groups
- [ ] No duplicate imports

**Example properly organized:**
```python
# Standard library
import asyncio
import json
from datetime import datetime
from typing import Any, Optional

# Third-party
import sqlalchemy as sa
from fastapi import FastAPI
from pydantic import BaseModel

# Local
from backend.db.models import ScanRun
from backend.utils.logger import get_logger
```

**If fails:** Run `isort <file>` to auto-fix

---

## ✅ CHECKLIST 2: Docstrings & Comments

Use after code quality checks pass.

### 2.1 Module-Level Docstring

**Check each Python file starts with:**
```python
"""Module description.

Explain what this module does, what classes/functions it contains,
and how to use it.

Example:
    Basic usage example here.
"""
```

**Verification checklist:**
- [ ] Module docstring exists at top
- [ ] Describes module purpose
- [ ] Lists main classes/functions
- [ ] Includes usage example if not obvious

### 2.2 Class Docstrings

**Every class must have docstring:**
```python
class RiskScoringEngine:
    """Calculates risk scores for vulnerabilities.
    
    Uses CVSS v3.1 scoring with organizational weighting factors
    to produce final risk score between 0-100.
    
    Attributes:
        weights (dict): Custom weighting factors
        redis_client: Cache backend
        
    Example:
        >>> engine = RiskScoringEngine()
        >>> score = engine.calculate_risk(vuln_data)
    """
```

**Verification checklist:**
- [ ] Docstring immediately after `class` line
- [ ] Describes class purpose (1-2 sentences)
- [ ] Documents key attributes if any
- [ ] Includes usage example
- [ ] Format: Google style (sections: Args, Returns, Raises, Example)

### 2.3 Function Docstrings

**Every function must have docstring:**
```python
def calculate_risk(
    self,
    vulnerability: VulnerabilityData,
    context: dict[str, Any] | None = None
) -> float:
    """Calculate risk score for vulnerability.
    
    Normalizes CVSS v3.1, applies weighting, incorporates threat intel.
    Results cached in Redis for performance.
    
    Args:
        vulnerability: Vulnerability data including CVSS vector
        context: Optional organizational context (industry, location)
        
    Returns:
        Risk score as float between 0-100
        
    Raises:
        ValueError: If CVSS vector invalid
        CacheError: If Redis connection fails
        
    Example:
        >>> vuln = VulnerabilityData(cvss_score=7.5, Vector="...")
        >>> score = engine.calculate_risk(vuln)
        >>> assert 0 <= score <= 100
    """
```

**Verification checklist:**
- [ ] Docstring after function definition
- [ ] One-line summary (what it does)
- [ ] Longer description if complex
- [ ] Args section with each parameter
- [ ] Returns section with return type/value
- [ ] Raises section with exceptions
- [ ] Example section with usage

### 2.4 Complex Logic Comments

**Complex algorithms need inline comments:**
```python
async def calculate_risk(self, vuln: VulnerabilityData) -> float:
    """Calculate risk score."""
    
    # Step 1: Normalize CVSS v3.1 score to 0-100 scale
    normalized_cvss = self._normalize_cvss(vuln.cvss_score)
    
    # Step 2: Apply organizational weighting factors
    weighted_score = normalized_cvss * self.weights['severity']
    
    # Step 3: Incorporate threat intelligence (recent exploits increase score)
    if self._is_recently_exploited(vuln.cve_id):
        weighted_score *= 1.5  # 50% boost for active exploits
    
    # Step 4: Cap at 100
    return min(weighted_score, 100.0)
```

**Verification checklist:**
- [ ] Complex algorithms have comments
- [ ] Comments explain WHY, not WHAT
- [ ] Comments for non-obvious calculations
- [ ] Comments for business logic (weighting factors, thresholds)

---

## ✅ CHECKLIST 3: Test Coverage

Use after passing code quality.

### 3.1 Run Tests

**Check:**
```bash
pytest backend/tests/test_models.py -v --cov=backend.db.models --cov-report=term-missing
```

**Expected:**
```
============================= test session starts ==============================
...
============================== 95 passed in 0.50s ==============================
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
backend/db/models.py       100     5    95%    45-50, 120
```

**Verification checklist:**
- [ ] All tests pass (0 failures)
- [ ] Coverage is 90%+ minimum
- [ ] If below 90%, add tests for missing lines
- [ ] No warnings or deprecations

### 3.2 Coverage Report

**Generate full HTML report:**
```bash
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html  # macOS
```

**Verification checklist:**
- [ ] Open htmlcov/index.html in browser
- [ ] Red lines = uncovered code
- [ ] Green lines = covered code
- [ ] Each module >= 90% covered
- [ ] High-risk code (external APIs, auth) fully covered

### 3.3 Test Quality

**Each test file should have:**

```python
# backend/tests/test_models.py
import pytest
from sqlalchemy import create_engine

class TestScanRun:
    """Test suite for ScanRun model."""
    
    @pytest.fixture
    def db_session(self):
        """Provide test database session."""
        # ... setup
        yield session
        # ... teardown
    
    def test_scan_run_creation(self, db_session):
        """Test basic model instantiation."""
        assert True  # At least one test
    
    @pytest.mark.parametrize("status", [...])
    def test_status_transitions(self, db_session, status):
        """Test each status transition."""
        # Multiple scenarios with parametrized tests
```

**Verification checklist:**
- [ ] Fixtures properly defined in conftest.py or test file
- [ ] Tests use fixtures (not hardcoded setup)
- [ ] Happy path tested
- [ ] Edge cases tested
- [ ] Error cases tested
- [ ] Parametrized tests for multiple scenarios
- [ ] Each test has single responsibility
- [ ] Docstrings explain what's tested

### 3.4 Test Organization

**Test files follow pattern:**
```
backend/tests/
├── __init__.py
├── conftest.py                  # Shared fixtures
├── test_models.py              # Database model tests
├── test_orchestrator.py        # Orchestrator tests
├── test_intelligence.py        # Intelligence module tests
├── test_api.py                 # API endpoint tests
├── test_integration.py         # E2E integration tests
└── test_performance.py         # Performance benchmarks
```

**Verification checklist:**
- [ ] Test file exists for each module
- [ ] conftest.py has shared fixtures
- [ ] Test class per class (TestScanRun, TestSubdomain, etc.)
- [ ] Test method per scenario
- [ ] Naming: test_<what>_<scenario> (test_scan_run_creation)

---

## ✅ CHECKLIST 4: Integration Tests

Use after individual module tests pass.

### 4.1 Integration Test Coverage

**Verify integration works:**
```bash
pytest backend/tests/test_integration.py -v
```

**Example integration test:**
```python
@pytest.mark.asyncio
async def test_full_scan_workflow(self, db_session):
    """Test complete scanning orchestration."""
    # 1. Create scan
    scan = ScanRun(domain="example.com")
    db_session.add(scan)
    db_session.commit()
    
    # 2. Run discovery
    discovery = DiscoveryScanner()
    subdomains = await discovery.scan(scan)
    for subdomain in subdomains:
        db_session.add(subdomain)
    db_session.commit()
    
    # 3. Run port scan
    portscan = PortScanScanner()
    ports = await portscan.scan(scan.subdomains)
    # ... verify
    
    # 4. Verify results integrated correctly
    assert scan.subdomains[0].ports is not None
    assert len(scan.vulnerabilities) > 0
```

**Verification checklist:**
- [ ] Integration tests exercise multiple modules
- [ ] Data flows correctly between modules
- [ ] Database relationships work
- [ ] Async/await chains work
- [ ] Error handling in integrated system

### 4.2 API Integration Tests

**Verify API endpoints work:**
```bash
pytest backend/tests/test_api.py -v
```

**Example:**
```python
@pytest.mark.asyncio
async def test_create_scan_endpoint(self, client):
    """Test POST /scans endpoint."""
    response = await client.post(
        "/scans",
        json={"domain": "example.com", "scan_type": "full"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["domain"] == "example.com"
```

**Verification checklist:**
- [ ] All endpoints tested
- [ ] Request/response validation works
- [ ] HTTP status codes correct (201 for create, 200 for get, etc.)
- [ ] Error handling works (400 for bad input, 404 for not found, etc.)
- [ ] Authentication/authorization tested

---

## ✅ CHECKLIST 5: Documentation

Use when module complete.

### 5.1 README or Module Documentation

**For each major module, file should have:**
- Purpose description
- Key classes/functions
- Usage examples
- Configuration needed

**Example:**
```markdown
# Risk Scoring Engine

Calculates risk scores for vulnerabilities using CVSS v3.1 with organizational context.

## Classes

- `RiskScoringEngine`: Main class for risk calculation
- `RiskScore`: Data class for risk calculation result

## Usage

```python
from backend.intelligence.risk_scorer import RiskScoringEngine

engine = RiskScoringEngine()
score = await engine.calculate_risk(vulnerability_data)
```

## Configuration

- `RISK_WEIGHTS_SEVERITY`: Weight for severity (default 0.4)
- `RISK_WEIGHTS_EXPLOITABILITY`: Weight for exploitability (default 0.6)
- `REDIS_CACHE_TTL`: Cache duration in seconds (default 3600)
```

**Verification checklist:**
- [ ] README or docstring exists
- [ ] Purpose clearly stated
- [ ] Key classes/functions listed
- [ ] Usage examples provided
- [ ] Configuration options documented

### 5.2 Code Comments

**Complex sections need comments:**
- Algorithms and math: Explain the formula
- Business logic: Explain the rule
- Bug fixes: Link to issue or explain workaround
- Performance optimizations: Explain why this approach

**DO NOT comment obvious code:**
```python
❌ WRONG - Over-commenting:
x = 1  # Set x to 1
x += 2  # Add 2 to x

✅ RIGHT - Comment when needed:
# Normalize CVSS score to 0-100 scale
normalized_score = (cvss_score / 10.0) * 100

# Workaround for issue #1234 - older PySQL versions don't support this
# TODO: Remove when upgrading to PySQL 3.0
query = session.query(...)
```

**Verification checklist:**
- [ ] Complex algorithms commented
- [ ] Business logic explained
- [ ] Workarounds documented
- [ ] TODO items have issue references
- [ ] No obvious code over-commented

### 5.3 Type Hints as Documentation

**Type hints should be self-documenting:**

```python
❌ WEAK - No types:
def process(data):
    return data

✅ STRONG - Types document intent:
def process(data: dict[str, Any]) -> ProcessResult:
    """Process scan data and return result."""
    return ProcessResult(...)
```

**Verification checklist:**
- [ ] Type hints clear and specific
- [ ] Generic types use brackets (list[T], dict[K,V])
- [ ] Union types explicit (str | None not just str)
- [ ] Custom types imported and defined

---

## ✅ CHECKLIST 6: Performance

Use for performance-sensitive code.

### 6.1 Query Performance (Database)

**For database operations:**
```python
@pytest.mark.benchmark
def test_query_performance(self, db_session, benchmark):
    """Benchmark subdomain query performance."""
    def query():
        return session.query(Subdomain).filter_by(
            scan_id=1
        ).all()
    
    result = benchmark(query)
    assert len(result) > 0

# Run: pytest backend/tests/test_performance.py -v --benchmark-only
```

**Verification checklist:**
- [ ] Frequently-used queries are indexed
- [ ] N+1 queries eliminated (use joinedload)
- [ ] Large result sets paginated
- [ ] Query execution time < 100ms for basic queries

**Check query plans:**
```bash
# In PostgreSQL shell
EXPLAIN ANALYZE SELECT * FROM subdomains WHERE scan_id = 1;
# Should show "Index Scan" not "Sequential Scan"
```

### 6.2 API Response Time

**API endpoints should respond quickly:**
```python
@pytest.mark.asyncio
async def test_get_scan_response_time(self, client, benchmark_async):
    """Verify GET /scans/{id} under 200ms."""
    async def endpoint():
        return await client.get("/scans/1")
    
    result = await benchmark_async(endpoint)
    assert result.status_code == 200
```

**Verification checklist:**
- [ ] Simple GET requests < 100ms
- [ ] Complex queries < 500ms
- [ ] Create operations < 500ms (includes DB write)
- [ ] Bulk operations < 2s

### 6.3 Memory Usage

**For large operations, check memory:**
```python
import tracemalloc

tracemalloc.start()
result = await orchestrator.scan(large_domain_list)
current, peak = tracemalloc.get_traced_memory()
print(f"Memory: {peak / 1024 / 1024:.1f}MB")
tracemalloc.stop()
```

**Verification checklist:**
- [ ] Memory usage reasonable for operation size
- [ ] No memory leaks (peak usage returns to baseline after operation)
- [ ] Large scans don't consume > 1GB RAM

---

## ✅ CHECKLIST 7: Security

Use for security-sensitive code.

### 7.1 SQL Injection Prevention

**Verification:**
```python
❌ WRONG - SQL injection vulnerable:
query = f"SELECT * FROM vulnerabilities WHERE cve_id = '{cve_id}'"
result = session.execute(query)

✅ CORRECT - Parameterized:
result = await session.execute(
    select(Vulnerability).where(Vulnerability.cve_id == cve_id)
)
```

**Verification checklist:**
- [ ] All database queries use ORM (no f-strings in SQL)
- [ ] User input never interpolated into SQL
- [ ] Parameters passed separately from query

### 7.2 Authentication & Authorization

**Verification:**
```python
@router.get("/scans/{scan_id}")
async def get_scan(
    scan_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> ScanResponse:
    """Get scan only if user has permission."""
    # Verify user can access this scan
    if not current_user.can_view_scan(scan_id):
        raise HTTPException(status_code=403)
    
    scan = await session.get(ScanRun, scan_id)
    if not scan:
        raise HTTPException(status_code=404)
    return ScanResponse.from_orm(scan)
```

**Verification checklist:**
- [ ] All protected endpoints verify authentication
- [ ] All endpoints verify authorization (user can access resource)
- [ ] API keys properly validated
- [ ] JWT tokens properly signed and verified
- [ ] Passwords hashed (bcrypt or similar)
- [ ] No passwords logged or exposed in errors

### 7.3 Input Validation

**Verification:**
```python
class ScanCreateRequest(BaseModel):
    """Validate scan creation input."""
    domain: str = Field(..., min_length=1, max_length=255)
    # Regex for domain validation
    @validator('domain')
    def validate_domain(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Domain cannot be empty")
        return v.lower()
```

**Verification checklist:**
- [ ] All user input validated
- [ ] Input length limits enforced
- [ ] Input type validation (Pydantic models)
- [ ] No code injection possible (inputs treated as data)
- [ ] Error messages don't leak sensitive info

### 7.4 Sensitive Data Handling

**Verification:**
```python
❌ WRONG - API key in logs:
logger.info(f"Connecting to API with key {api_key}")

✅ CORRECT - Redact sensitive data:
logger.info("Connecting to VirusTotal API")
# Keep API key in environment variable
api_key = os.getenv("VIRUSTOTAL_API_KEY")
```

**Verification checklist:**
- [ ] API keys and secrets in environment, not code
- [ ] Passwords never logged
- [ ] Database credentials never logged
- [ ] Error messages don't expose sensitive paths
- [ ] No PII (personally identifiable information) in logs

---

## ✅ CHECKLIST 8: Final Verification

Use before committing code.

### 8.1 Complete Quality Gates

```bash
# Run everything at once
make quality && make test

# Output should show:
# ✅ mypy: Success
# ✅ black: All done
# ✅ flake8: [no output]
# ✅ isort: [no output]
# ✅ pytest: X passed in Ys
```

**Verification checklist:**
- [ ] mypy passes with 0 errors
- [ ] black passes with 0 changes needed
- [ ] flake8 passes with 0 violations
- [ ] isort passes with 0 changes needed
- [ ] pytest passes with 90%+ coverage
- [ ] All tests pass (0 failures, 0 skipped)

### 8.2 Code Review Checklist

Before saving to file, review:
- [ ] Imports organized (stdlib, 3rd party, local)
- [ ] No unused imports
- [ ] No hardcoded values (use config/env)
- [ ] Error handling present for external calls
- [ ] Docstrings comprehensive and clear
- [ ] Type hints complete (100%)
- [ ] Tests cover happy path, edge cases, errors
- [ ] Test coverage 90%+
- [ ] No commented-out code
- [ ] No debug print statements
- [ ] No TODO without issue reference
- [ ] Variable names clear and descriptive
- [ ] Functions/methods have single responsibility
- [ ] No code duplication (DRY principle)

### 8.3 Git Commit Checklist

Before committing:
- [ ] All quality gates pass locally
- [ ] Code compiles/imports without error
- [ ] Tests pass with meaningful failure messages if any (0 expected)
- [ ] Commit message clear and descriptive
- [ ] Only intended files included in commit
- [ ] No temporary files or artifacts committed
- [ ] Related issue numbers referenced in commit message

**Example commit:**
```bash
git add backend/db/models.py backend/tests/test_models.py
git commit -m "feat(models): Add ScanRun and Subdomain models

- ScanRun as parent scan record with timestamps
- Subdomain with many-to-one relationship to ScanRun
- Full type hints and Google-style docstrings
- 95% test coverage with relationship tests

Closes #42"
```

### 8.4 Final Checklist

Before moving to next prompt:
- [ ] Code saved to correct file
- [ ] All quality gates pass (make quality)
- [ ] All tests pass (make test) with 90%+ coverage
- [ ] Code reviewed (self-review checklist)
- [ ] Git committed with clear message
- [ ] README updated if new module or breaking changes
- [ ] Next prompt identified
- [ ] Dependencies for next prompt documented

---

## 📊 Quality Gate Summary Table

| Gate | Command | Success Criteria |
|------|---------|------------------|
| Type Hints | `mypy . --strict` | 0 errors |
| Formatting | `black . --check` | "All done!" |
| Linting | `flake8 .` | [Empty output] |
| Imports | `isort . --check-only` | [Empty output] |
| Tests | `pytest . --cov=. --cov-fail-under=90` | 90%+ coverage, 0 failures |
| Integration | `pytest tests/test_integration.py` | All pass |
| Performance | Custom benchmarks | No regressions |
| Security | Manual + tools | All issues fixed |

---

## 🚀 Daily Verification Routine

**Each morning when resuming work:**

```bash
# 1. Check what changed
git status

# 2. Verify previously saved code still works
make test

# 3. Run full quality gates
make quality

# 4. If all pass → Ready to start new prompt
# If any fail → Check error-recovery.md
```

---

**Last updated:** February 2026  
**Related:** [claude.md](claude.md), [restrictions.md](restrictions.md), [error-recovery.md](error-recovery.md)
