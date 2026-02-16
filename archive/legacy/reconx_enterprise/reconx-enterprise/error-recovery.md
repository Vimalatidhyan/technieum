# 🚨 Error Recovery Guide - Claude Code Generation

**Purpose:** Troubleshoot and fix when generated code fails quality gates

**Version:** v2.0  
**Scope:** Type errors, test failures, quality violations, runtime errors

---

## 🔍 General Troubleshooting Workflow

```
Generated code → Paste to file → Run quality gates
    ↓
Quality gate fails
    ↓
Read error message carefully
    ↓
Go to error type section below
    ↓
Follow fix steps
    ↓
Show Claude the error (copy-paste it)
    ↓
Claude fixes code
    ↓
Rerun quality gates
    ↓
Success → Move to next prompt
```

---

## ❌ ERROR TYPE 1: Type Hints (mypy errors)

**Symptom:** `mypy` reports missing type annotations or type mismatches

### Error: "missing return type"

```
error: Missing return type annotation for function "calculate_risk"  [no-untyped-def]
```

**What it means:** Function doesn't have return type annotation

**Fix:**
```python
❌ WRONG:
def calculate_risk(vuln):
    return 100.0

✅ CORRECT:
def calculate_risk(vuln: Vulnerability) -> float:
    return 100.0
```

**Action:**
1. Find the function in error message
2. Copy the error: `...missing return type...`
3. Tell Claude: `mypy reports: "missing return type annotation for function calculate_risk". Fix it.`
4. Claude regenerates function with type hints
5. Replace function in file
6. Rerun: `mypy backend/ --strict`

### Error: "Argument of type X cannot be assigned to parameter of type Y"

```
error: Argument 1 to "query" of "Session" has incompatible type "type[Vulnerability]"; expected "FromClause"
```

**What it means:** You're passing wrong type to function

**Fix:**
1. Check the function signature where error occurs
2. Usually: wrong Model being passed, or async/sync confusion
3. Tell Claude: `mypy says: "Argument 1 to 'query' has incompatible type". The Session.query expects FromClause, not type.`
4. Claude fixes by using correct SQLAlchemy syntax

### Error: "Incompatible return value type"

```
error: Incompatible return value type (got "[Vulnerability]", expected "Vulnerability")
```

**What it means:** Returning wrong type (list instead of single item, or vice versa)

**Fix:**
```python
❌ WRONG:
async def get_vulnerability(vuln_id: int) -> Vulnerability:
    result = await session.execute(select(Vulnerability).where(...))
    return result.scalars().all()  # Returns list, not single item

✅ CORRECT:
async def get_vulnerability(vuln_id: int) -> Vulnerability:
    result = await session.execute(select(Vulnerability).where(...))
    return result.scalar_one_or_none()  # Returns single item
```

**Action:**
1. Look at return type annotation in error
2. Look at what code is actually returning
3. Tell Claude: `mypy: "Incompatible return value type (got 'list[Vulnerability]', expected 'Vulnerability')"`
4. Claude fixes return statement

### Error: "Can't determine type of..."

```
error: Cannot determine type of "result" (reportGeneralTypeIssues)
```

**What it means:** mypy can't figure out the type from context

**Fix:** Add explicit type annotation:
```python
❌ WRONG:
result = await fetch_data()  # mypy can't tell what type result is

✅ CORRECT:
result: list[ScanRun] = await fetch_data()  # explicit type
```

**Action:**
1. Add type annotation to the variable
2. Tell Claude: `mypy: "Cannot determine type of 'result'". Add explicit type annotation.`
3. Claude adds type hint

### Error: "Need type annotation for..."

```
error: Need type annotation for "vulnerability" (name defined without default) [var-annotated]
```

**What it means:** Variable lacks type annotation

**Fix:**
```python
❌ WRONG:
for vulnerability in vulnerabilities:
    score = vulnerability.cvss

✅ CORRECT:
for vulnerability in vulnerabilities:
    score: float = vulnerability.cvss
```

**Action:**
1. Show Claude exact error with line number
2. Tell Claude: `mypy: "Need type annotation for 'score'". Add type hints to all variables.`
3. Claude adds annotations

---

## ❌ ERROR TYPE 2: Test Failures (pytest errors)

**Symptom:** `pytest` reports test failures

### Error: "FAILED test_models.py::TestScanRun::test_scan_run_creation"

```
AssertionError: assert 'pending' == 'PENDING'
```

**What it means:** Test assertion failed

**Fix:**
1. Read the assertion: Expected 'PENDING' but got 'pending'
2. The ScanStatus enum values might be uppercase
3. Tell Claude: `Test fails: expected 'PENDING' but got 'pending'. Check if ScanStatus enum uses uppercase.`
4. Claude fixes code to match expected values

### Error: "ImportError: cannot import name X from Y"

```
ImportError: cannot import name 'ScanRun' from 'backend.db.models'
```

**What it means:** Can't find the imported class

**Fix possibilities:**
1. Model not created yet → Create earlier prompt first
2. Wrong import path → Check __init__.py exports
3. Typo in class name → Check spelling

**Action:**
1. Verify file exists: `ls -la backend/db/models.py`
2. Check it has the class: `grep "class ScanRun" backend/db/models.py`
3. If not there, complete that prompt first
4. If there, tell Claude: `ImportError: "cannot import name 'ScanRun'". Check __init__.py exports and spelling.`

### Error: "Fixture 'db_session' not found"

```
fixture 'db_session' not found
```

**What it means:** Test references fixture that doesn't exist

**Fix:**
1. Add fixture to conftest.py:
```python
# backend/tests/conftest.py
@pytest.fixture
def db_session():
    """Provide test database session."""
    # ... fixture implementation
    yield session
    # cleanup
```

2. Tell Claude if fixture needs different setup

### Error: "Test coverage below 90%"

```
Name                               Stmts   Miss  Cover   Missing
─────────────────────────────────────────────────────────────────
backend/db/models.py                100    15    85%    12-25, 45-67
```

**What it means:** Tests don't cover all code. Need 90%+

**Fix:**
1. Check coverage report: `pytest backend/ --cov-report=html`
2. Open `htmlcov/index.html` to see which lines aren't tested
3. Add tests for missing lines
4. Tell Claude: `Coverage is 85%, need 90%+. Missing tests for lines 12-25 in ScanRun model.`
5. Claude adds tests for missing coverage

### Error: "xfail marker not found"

```
marker 'xfail' not found
```

**What it means:** Test has @pytest.mark.xfail but pytest not configured for it

**Fix:** Check pytest.ini or pyproject.toml has config

### Error: "Timeout: test didn't complete"

```
Timeout: test_long_operation exceeded timeout of 30 seconds
```

**What it means:** Async test took too long

**Fix:**
1. Add timeout to test: `@pytest.mark.timeout(60)`
2. Or fix the operation to be faster
3. Tell Claude: `Test times out. Add a 60s timeout or optimize query.`

---

## ❌ ERROR TYPE 3: Code Quality (black, flake8, isort)

**Symptom:** `black`, `flake8`, or `isort` report violations

### Error: "line too long (100 > 88 characters)"

```
E501 line too long (100 > 88) [line 42]
```

**What it means:** Line exceeds 88 character limit

**Fix:**
```python
❌ WRONG (95 chars):
vulnerabilities = await session.execute(select(Vulnerability).where(Vulnerability.cvss_score > 7.0))

✅ CORRECT (split to multiple lines):
query = select(Vulnerability).where(
    Vulnerability.cvss_score > 7.0
)
vulnerabilities = await session.execute(query)
```

**Action:**
1. Run `black backend/` → auto-fixes most formatting
2. If line still too long, split it manually
3. Tell Claude: `Line too long on line 42. Split into multiple lines.`

### Error: "module level import not at top of file"

```
E402 module level import not at top of file
```

**What it means:** Import statement not at top of file

**Fix:**
```python
❌ WRONG:
def setup():
    import json  # Import inside function

✅ CORRECT:
import json  # Import at top

def setup():
    pass
```

**Action:**
1. Move all imports to top of file
2. Run `isort backend/` → auto-organizes imports

### Error: "unused import"

```
F401 'requests' imported but unused
```

**What it means:** Imported module not used in code

**Fix:**
```python
❌ WRONG:
import requests  # Not used
import json

def process():
    return json.dumps({})

✅ CORRECT:
import json

def process():
    return json.dumps({})
```

**Action:**
1. Remove unused imports
2. Or prefix with underscore if intentionally kept: `import requests as _requests`
3. Run `autoflake --in-place --recursive backend/`

### Error: "trailing whitespace"

```
W291 trailing whitespace
```

**What it means:** Whitespace at end of line

**Fix:**
1. Run `black backend/` → auto-fixes
2. Or manually remove spaces at line end

### Error: "multiple statements on one line"

```
E704 multiple statements on one line (colon)
```

**What it means:** Multiple Python statements on same line

**Fix:**
```python
❌ WRONG:
x = 1; y = 2; return x + y

✅ CORRECT:
x = 1
y = 2
return x + y
```

### Error: "imports not alphabetically sorted"

```
isort says: ~/backend/utils/helpers.py (1 file would be reformatted)
```

**What it means:** Import statements not in correct order

**Fix:**
1. Run `isort backend/` → auto-sorts imports

---

## ❌ ERROR TYPE 4: Runtime Errors

**Symptom:** Code runs but crashes during execution

### Error: "AttributeError: 'ScanRun' object has no attribute 'domain'"

```
AttributeError: 'ScanRun' object has no attribute 'domain'
```

**What it means:** Attribute doesn't exist on model

**Cause 1 - Attribute not defined in model:**
```python
❌ WRONG:
class ScanRun:
    id: int  # Missing domain attribute

✅ CORRECT:
class ScanRun:
    id: int
    domain: str  # Add the attribute
```

**Cause 2 - Lazy loading not finished:**
```python
❌ WRONG - If domain uses lazy="select":
scan = session.query(ScanRun).get(1)
# Session closed
print(scan.domain)  # Error: session gone

✅ CORRECT - Eager load or access within session:
scan = session.query(ScanRun).options(joinedload(ScanRun.domain)).get(1)
```

**Action:**
1. Check model definition has the attribute
2. Tell Claude: `Runtime error: 'ScanRun' has no attribute 'domain'. Verify model definition.`

### Error: "KeyError: 'domain' - Dictionary key not found"

```
KeyError: 'domain'
```

**What it means:** Trying to access missing dictionary key

**Fix:**
```python
❌ WRONG:
data = {}
print(data['domain'])  # Key doesn't exist

✅ CORRECT:
data = {}
print(data.get('domain', 'unknown'))  # Safe access with default
```

**Action:**
1. Use `.get()` instead of `[key]` for optional keys
2. Tell Claude: `KeyError: 'domain'. Use .get() for safe dictionary access.`

### Error: "TypeError: unsupported operand type(s) for +: 'str' and 'int'"

```
TypeError: unsupported operand type(s) for +: 'str' and 'int'
```

**What it means:** Trying to add incompatible types

**Fix:**
```python
❌ WRONG:
result = "score: " + 100  # Can't add str + int

✅ CORRECT:
result = f"score: {100}"  # Use f-string
# or
result = "score: " + str(100)
```

**Action:**
1. Tell Claude: `TypeError: can't add 'str' and 'int'. Use f-strings or str() conversion.`

### Error: "asyncio.InvalidStateError: another task is pending"

```
asyncio.InvalidStateError: another task is pending
```

**What it means:** Async state management issue

**Fix:**
1. Make sure to `await` all async calls
2. Use `async with` for context managers
3. Check for orphaned tasks

**Action:**
1. Tell Claude: `InvalidStateError: inconsistent async/await. Verify all async operations are awaited.`

### Error: "sqlalchemy.exc.IntegrityError: Foreign key constraint fails"

```
sqlalchemy.exc.IntegrityError: (psycopg2.errors.ForeignKeyViolation)
```

**What it means:** Trying to create record with invalid foreign key reference

**Fix:**
```python
❌ WRONG:
subdomain = Subdomain(scan_id=999)  # No ScanRun with id=999
session.add(subdomain)
session.commit()  # Fails: scan_id doesn't exist

✅ CORRECT:
scan = ScanRun(domain="example.com")
session.add(scan)
session.commit()
subdomain = Subdomain(scan_id=scan.id)  # Valid reference
session.add(subdomain)
session.commit()
```

**Action:**
1. Ensure parent record exists before creating child
2. In tests, use fixtures to create required parent records
3. Tell Claude: `IntegrityError on foreign key. Ensure parent ScanRun exists before adding Subdomain.`

### Error: "ConnectionError: can't connect to Redis"

```
ConnectionError: Error -2 connecting to localhost:6379
```

**What it means:** Redis not running or connection failed

**Fix:**
1. Check if Redis is running: `docker-compose ps | grep redis`
2. Start if not running: `docker-compose up -d redis`
3. Check connection: `redis-cli ping` → should return "PONG"

**Action:**
1. Verify Redis is up: `docker-compose up -d redis`
2. Verify connection in code with retry logic
3. Tell Claude: `ConnectionError to Redis. Add retry logic and connection pooling.`

---

## 🔧 QUICK FIX COMMANDS

```bash
# Auto-fix most Python issues:
black backend/
isort backend/
autoflake --in-place --remove-all-unused-imports --recursive backend/

# Check what needs fixing:
mypy backend/ --strict 2>&1 | head -20
flake8 backend/ 2>&1 | head -20
pytest backend/tests/ -x -v  # Stop on first failure

# Full quality check:
make quality

# Coverage report:
pytest backend/ --cov=backend --cov-report=html
open htmlcov/index.html  # On macOS
```

---

## 📋 Error Recovery Checklist

When code fails:

- [ ] **Read error message completely** - Don't skip details
- [ ] **Identify error type** - Type hint? Test? Runtime? Quality?
- [ ] **Find the line number** - Locate exact problem location
- [ ] **Understand root cause** - Why did it fail?
- [ ] **Copy the error message** - Paste to Claude
- [ ] **Show Claude context** - Include relevant code from file
- [ ] **Tell Claude to regenerate** - "Fix this error and regenerate the [function/class/file]"
- [ ] **Get fixed code** - Claude provides corrected version
- [ ] **Replace in file** - Complete file, not just snippet
- [ ] **Rerun test** - Verify fix works
- [ ] **Move forward** - Next prompt or verification step

---

## 🆘 Still Stuck?

### Option 1: Show Claude More Context

```
You: "mypy says: 'Missing return type annotation for calculate_risk'.
     Here's the function:
     [paste entire function from file]
     Here's how it's used:
     [paste calling code]
     Fix it and regenerate the entire function."
```

Claude can fix better with more context.

### Option 2: Break Into Smaller Pieces

If large function has multiple issues:

```
You: "Generate just the __init__ method first with all type hints and docstrings."
Claude: [generates init]

You: "Now generate the calculate_risk method..."
Claude: [generates that method]

You: "Now generate full test suite..."
Claude: [generates tests]
```

Smaller pieces easier to debug.

### Option 3: Compare with Working Code

```
You: "Here's the working ScanRun model:
     [paste working code from backend/db/models.py]
     
     Here's the broken Subdomain model:
     [paste broken code]
     
     Make Subdomain consistent with ScanRun pattern."
```

### Option 4: Reset and Regenerate

If code is too broken:

1. Don't save to file yet
2. Copy just the prompt (from COMPLETE_SEQUENTIAL_PROMPTS.md)
3. Paste fresh prompt to Claude
4. Get fresh generation
5. Save to file
6. Test again

---

## 🎯 Prevention Tips

### Tip 1: Test Incrementally
```bash
# Don't wait until end - test as you go
mypy backend/db/models.py --strict
pytest backend/tests/test_models.py -v
```

### Tip 2: Copy Complete Prompts
Don't paraphrase. Copy **exact** prompt text from COMPLETE_SEQUENTIAL_PROMPTS.md.

### Tip 3: Ask for Clarifications
If prompt is ambiguous, ask Claude:
- "Should this function retry on timeout?"
- "What should happen if validation fails?"
- "Do we cache this result in Redis?"

### Tip 4: Review Generated Code
Before saving:
1. Skim through imports - look reasonable?
2. Check docstrings - are they meaningful?
3. Spot check type hints - are they complete?
4. Glance at tests - do they make sense?

### Tip 5: Keep Versions
Before running tests on changed file:
1. Save current version: `cp backend/db/models.py backend/db/models.py.bak`
2. Test new version
3. If broken, recover: `cp backend/db/models.py.bak backend/db/models.py`
4. Regenerate with Claude

---

## 📞 When to Ask for Help

### Ask Claude:
- Type hint questions: "How do I type hint a function that returns either X or None?"
- Architecture questions: "Should this be async or sync?"
- Design questions: "How should ScanRun and Vulnerability relate?"

### Ask in GitHub Issues:
- Reproducible bugs: "When I run [command], I get [error]"
- Ambiguous requirements: "The spec doesn't say how to handle [scenario]"
- Build environment: "Docker container won't start"

### Look in Docs:
- Database schema: [Database context](prompts-design/week-3-week-4-context.md)
- Architecture: [Architecture decisions](docs/ARCHITECTURE_DECISIONS.md)
- API design: [API specifications](prompts-design/week-11-week-12-context.md)

---

**Last updated:** February 2026  
**For system message:** See [claude.md](claude.md)  
**For constraints:** See [restrictions.md](restrictions.md)
