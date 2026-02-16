# Quality Gates & Verification Checklist
## How to Ensure Production-Ready Code from AI Agents

---

## 🎯 Philosophy

**Every AI-generated code MUST pass quality gates before moving forward.**

*Quality gates prevent: bugs, technical debt, inconsistent style, poor testing*

*They enable: confidence in code, faster merges, fewer regressions*

---

## 🚦 Pre-Commit Checklist (Before Each Git Commit)

### Level 1: Does it Run? (5 minutes)

#### Test: No Import Errors
```bash
# For Python modules
python -c "from backend.db.models import ScanRun"

# For entire package
python -m py_compile backend/db/models.py

# Look for: 0 errors
# Typical time: <30 seconds
```

✅ **Pass:** No output = no errors
❌ **Fail:** `ModuleNotFoundError`, `SyntaxError`, etc.

#### Test: Type Checking
```bash
# Check if types are valid
mypy backend/db/models.py

# Look for: 0 errors found in [file]
# Typical time: 2-5 minutes
```

✅ **Pass:** `Success: no issues found`
❌ **Fail:** `error: ...` messages

### Level 2: Does it Meet Code Standards? (5 minutes)

#### Test: Code Style (PEP 8)
```bash
# Check formatting
flake8 backend/db/models.py --max-line-length=88

# Look for no output = no violations
```

✅ **Pass:** No output (clean code)
❌ **Fail:** `E501 line too long`, `F401 imported but unused`, etc.

#### Test: Format with Black
```bash
# Auto-format file
black backend/db/models.py

# Check: No changes made means file was already formatted
```

✅ **Pass:** Up to date with black style
❌ **Fail:** File gets reformatted (wasn't following style)

#### Test: Import Sorting
```bash
# Check import order
isort --check-only backend/db/models.py

# Or auto-fix
isort backend/db/models.py
```

✅ **Pass:** Imports organized correctly
❌ **Fail:** Imports out of order

#### Test: All at Once
```bash
# Run all linting
make lint

# Or individual
black backend/
flake8 backend/
isort backend/
```

### Level 3: Tests Pass? (Variable, depends on scope)

#### Test: Unit Tests for This Feature
```bash
# Test ONLY the feature you just created
pytest backend/tests/test_models.py::test_scanrun -v

# Look for: PASSED (all tests green)
# Typical time: 10-30 seconds per test file
```

✅ **Pass:** `passed` in output
❌ **Fail:** `FAILED` in output → need to fix code

#### Test: Related Integration Tests
```bash
# If you created/modified API endpoint
pytest backend/tests/test_api_scans.py -v

# If you modified database layer
pytest backend/tests/test_database.py -v
```

✅ **Pass:** All related tests pass
❌ **Fail:** Broken tests → don't commit yet

#### Test: Full Test Suite
```bash
# Run all tests before merge
make test

# Or
pytest backend/tests/ -v

# Look for: X passed, 0 failed
```

✅ **Pass:** All tests pass
❌ **Fail:** Any test fails → debug first

### Level 4: Coverage Adequate? (2 minutes)

#### Test: Code Coverage
```bash
# Generate coverage report
pytest --cov=backend --cov-report=term-missing backend/tests/

# Look for: >85% coverage overall
```

**Example output:**
```
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
backend/db/models.py                50      2    96%   45, 78
backend/api/routes/scans.py        120      8    93%   45-48, 234-236
...
TOTAL                            2400     240    90%
```

✅ **Pass:** 85%+ coverage (preferably >90%)
❌ **Fail:** <85% coverage → need more tests

#### Specifically for New Code
```bash
# Coverage of changes only
pytest --cov=backend --cov-report=term-missing --cov-report=html

# Then check: Open htmlcov/index.html
# Look for: New code highlighted green (tested)
```

✅ **Pass:** All new code green (tested)
❌ **Fail:** Any new code red (untested)

### Level 5: Docstrings Present? (5 minutes)

#### Test: Documentation Coverage
```bash
# Check for missing docstrings
pylint backend/db/models.py --disable=all --enable=missing-docstring

# Or use flake8 plugin
flake8 --select=D backend/db/models.py  # requires flake8-docstrings
```

✅ **Pass:** No missing docstring warnings
❌ **Fail:** `D100 Missing docstring` warnings

#### Manual Review
```python
# ✅ CORRECT: All public functions have docstrings
class ScanRun(Base):
    """Represents a scanning task execution."""
    
    def get_duration(self) -> int:
        """Calculate duration in seconds."""
        pass

# ❌ WRONG: Missing docstring
class ScanRun(Base):
    def get_duration(self) -> int:
        pass
```

### Level 6: Type Hints Present? (5 minutes)

#### Manual Review
```python
# ✅ CORRECT: All parameters and returns typed
def calculate_risk(vulns: List[Dict[str, Any]]) -> float:
    pass

# ✅ CORRECT: Class methods typed
class ScanRun(Base):
    def get_severity(self) -> int:
        pass

# ❌ WRONG: Missing types
def calculate_risk(vulns):  # No param types!
    pass

def get_severity(self):  # No return type!
    pass
```

#### Test: Type Checking
```bash
# Validate all types
mypy backend/db/models.py --strict

# Look for: Success: no issues found
```

---

## 🔍 Feature-Specific Checks

### For Database Models

```bash
# ✅ Must have:
- [ ] Docstring explaining purpose
- [ ] All fields typed
- [ ] Primary key defined
- [ ] Important fields indexed
- [ ] Relationships with back_populates
- [ ] __repr__() method
- [ ] Tests creating and querying

# Run:
pytest backend/tests/test_models.py -v
mypy backend/db/models.py
flake8 backend/db/models.py
```

### For API Endpoints

```bash
# ✅ Must have:
- [ ] Request model (Pydantic)
- [ ] Response model defined
- [ ] Status codes specified
- [ ] Docstring with Args/Returns
- [ ] Input validation
- [ ] Error handling (HTTPException)
- [ ] Tests for success & failure cases

# Run:
pytest backend/tests/test_api_*.py -v
mypy backend/api/routes/*.py
make lint
```

### For Tests

```bash
# ✅ Must have:
- [ ] Descriptive test names (test_<scenario>)
- [ ] Docstring explaining what's tested
- [ ] Fixtures for setup
- [ ] Both success & failure cases
- [ ] Specific assertions (not just assert True)
- [ ] No hardcoded data

# Run:
pytest backend/tests/test_*.py -v --cov
pytest --cov=backend --cov-report=html
```

---

## 📊 Pre-Commit Quality Report

**Before each git commit, fill this out:**

```markdown
## Quality Gate Report

Date: [DATE]
Feature: [What was created/fixed]
Files: [List modified files]

### Build Status
- [ ] All imports work (python -c)
- [ ] Type check passes (mypy)
- [ ] Code style correct (black, flake8)
- [ ] Test suite passes (pytest)

### Coverage
- [ ] Overall coverage >85%: [_]%
- [ ] New code tested: [GREEN/YELLOW/RED]

### Documentation
- [ ] Docstrings present: [YES/PARTIAL/NO]
- [ ] Type hints present: [YES/PARTIAL/NO]
- [ ] Comments explain WHY (not WHAT): [YES/NO]

### Testing
- [ ] Unit tests written: [YES/NO]
- [ ] Edge cases covered: [YES/PARTIAL/NO]
- [ ] Integration tests pass: [YES/NO]

### Code Quality
- [ ] No hardcoded values: [YES/NO]
- [ ] No security issues found: [YES/NO]
- [ ] Error handling present: [YES/PARTIAL/NO]
- [ ] Follows project patterns: [YES/NO]

### Sign-Off
Developer: _________
Reviewer (if applicable): _________
```

---

## ⚙️ Automated Quality Checks (Makefile)

```bash
# Run everything at once
make quality

# Or individual commands
make lint          # Black, flake8, isort
make type-check    # mypy assertions
make test          # pytest all
make coverage      # Coverage report
make docs-check    # Docstring check
```

---

## 🐛 Common Failures & Fixes

### Problem: Tests Fail

```bash
pytest backend/tests/test_models.py::test_scanrun -v

# Output:
FAILED test_models.py::test_scanrun - AssertionError: assert 'pending' == 'active'
```

**Solution:**
1. Read the error message (it tells you what's wrong)
2. Look at the test: what does it expect?
3. Look at the code: what's it actually doing?
4. Fix the code to match test expectations

**Example:**
```python
# Test expects this:
def test_scanrun_default_status():
    scan = ScanRun(domain="test.com")
    assert scan.status == "pending"  # ← Test expects "pending"

# But code does this:
class ScanRun(Base):
    status = Column(String(50), default="active")  # ← Oops! "active"

# Fix:
status = Column(String(50), default="pending")  # ✅ Now matches
```

### Problem: Type Check Fails

```bash
mypy backend/api/routes/scans.py

# Output:
scans.py:25: error: Incompatible types in assignment (expression has type "str", variable has type "int")
```

**Solution:**
1. Go to line 25
2. Find the type mismatch
3. Either change code or annotation

**Example:**
```python
# Line 25: Fails type check
severity: int = "high"  # ❌ Can't assign str to int

# Fix option 1: Use correct type
severity: str = "high"  # ✅

# Fix option 2: Cast value
severity: int = convert_to_int("high")  # ✅
```

### Problem: Coverage Too Low

```bash
pytest --cov=backend backend/tests/

# Output:
TOTAL    2400     400     83%  # ❌ Below 85%
```

**Solution:**
1. Find which file has lowest coverage
2. Write tests for untested code
3. Run again

**Example:**
```
backend/intelligence/risk_scorer.py  45%  ← Needs tests

# Create:
backend/tests/test_risk_scorer.py

# Write tests:
def test_calculate_risk_critical():
    result = calculate_risk([{"severity": "critical"}])
    assert result >= 75

def test_calculate_risk_multiple():
    ...
```

### Problem: Format/Style Issues

```bash
flake8 backend/db/models.py

# Output:
models.py:45:81: E501 line too long (92 > 88 characters)
```

**Solution:**
```python
# Too long:
description = "This is a very long description that exceeds the 88 character limit set by black"

# Fix:
description = (
    "This is a very long description that exceeds "
    "the 88 character limit set by black"
)

# Or use black to auto-fix:
black backend/db/models.py
```

---

## ✅ Sign-Off Checklist (Before Merge)

```
Code Review Gate:
- [ ] Code does what it should (tests pass)
- [ ] Follows style guide (make lint passes)
- [ ] Has documentation (docstrings present)
- [ ] Has tests (coverage >85%)
- [ ] No security issues (reviewed manually)
- [ ] No breaking changes (dependencies OK)

Commit Gate:
- [ ] Commit message semantic (feat: / fix: / etc)
- [ ] One logical change per commit
- [ ] All tests pass
- [ ] Ready for production

Merge Gate:
- [ ] Code review approved (if applicable)
- [ ] All CI checks passing
- [ ] Documentation updated
- [ ] CHANGELOG entry added
```

---

## 🎯 Quick Reference: Commands

### Before Every Commit

```bash
# 1. Does it run?
python -c "from backend.db.models import ScanRun"

# 2. Tests pass?
pytest backend/tests/ -v

# 3. Code formatted?
make lint

# 4. Types OK?
mypy backend/

# 5. Coverage good?
pytest --cov=backend backend/tests/

# 6. All good? Commit!
git commit -m "feat: <description>"
```

### During Development

```bash
# Watch tests as you code
pytest-watch backend/tests/  # Requires: pip install pytest-watch

# Or run specific test repeatedly
pytest backend/tests/test_models.py -v -s -x  # -x stops on first fail

# Check coverage while coding
pytest --cov=backend --cov-report=html backend/tests/
# Then open htmlcov/index.html in browser
```

### Weekly Review

```bash
# Full audit
make lint && make type-check && make test && make coverage

# If all pass: You're good!
# If anything fails: Fix before proceeding
```

---

## 🚨 When Quality Gates Fail

### Scenario 1: Test Fails

```
FAILED test_models.py::test_scanrun
    assert 'pending' == 'active'

DO NOT COMMIT!
FIX: Look at test, look at code, align them.
```

### Scenario 2: Coverage Too Low

```
backend/intelligence/risk_scorer.py  45%

DO NOT COMMIT!
FIX: Write more unit tests for untested code paths.
```

### Scenario 3: Type Check Fails

```
models.py:25: error: Incompatible types in assignment

DO NOT COMMIT!
FIX: Fix the type mismatch (str vs int, etc).
```

### Scenario 4: Style Issues

```
models.py:45:81: E501 line too long

DO NOT COMMIT!
FIX: Break long line, run `make lint` to auto-fix.
```

---

## 📈 Tracking Quality Over Time

**Every Friday, record:**

```markdown
## Week 3 Quality Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Coverage | 85%+ | 89% | ✅ PASS |
| All Tests Pass | 100% | 100% | ✅ PASS |
| Lint Errors | 0 | 0 | ✅ PASS |
| Type Errors | 0 | 0 | ✅ PASS |
| Code Issues | 0 | 0 | ✅ PASS |

**Result:** Week 3 code quality excellent! Ready to proceed.
```

---

## 🏅 Excellence Standards

### Gold Standard (Aim For This)
- ✅ 90%+ test coverage
- ✅ 0 type errors
- ✅ 0 lint errors
- ✅ All tests pass
- ✅ Full docstrings
- ✅ Comprehensive tests (success + failure + edge cases)

### Silver Standard (Minimum Acceptable)
- ✅ 85%+ test coverage
- ✅ 0 type errors (mypy strict mode)
- ✅ 0 lint errors
- ✅ All tests pass
- ✅ Docstrings on public functions
- ✅ Tests for main flows

### Not Acceptable
- ❌ <85% coverage
- ❌ Failing tests
- ❌ Type errors
- ❌ Lint errors
- ❌ Missing docstrings
- ❌ Code doesn't run

---

## 🎓 Summary

**Quality Gate = Stop and Verify Before Moving Forward**

Every feature must pass:
1. **Build gate** (imports work)
2. **Test gate** (tests pass)
3. **Style gate** (code formatted)
4. **Coverage gate** (85%+ tests)
5. **Documentation gate** (docstrings present)
6. **Type gate** (no type errors)

**Cost:** 15-20 minutes per task  
**Benefit:** Production-ready code, zero surprise bugs, confidence to refactor

**Golden Rule:** If quality gates fail, DO NOT COMMIT. Fix first.

---

**Your code quality standard: PROFESSIONAL GRADE**

*Speed comes from confidence. Confidence comes from quality gates.*

**You now have a complete quality assurance system!** ✅
