# 🤖 Claude Code Agent Guide - ReconX Enterprise v2.0

**Purpose:** Optimized instructions for Claude AI to generate production-grade code for ReconX Enterprise

**Target Model:** Claude 3.5 Sonnet (recommended for code generation quality)

---

## 🎯 Quick Start (30 seconds)

1. Open [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md)
2. Find your current prompt (e.g., PROMPT 3.1 for first task)
3. Copy the **entire prompt text** (everything in the code block)
4. Paste into Claude with this system message (see below)
5. Claude generates code → Copy to file → Run verification
6. Move to next prompt when current passes quality gates

---

## ⚙️ System Message for Claude

**Copy this and paste into Claude BEFORE your first prompt:**

```
You are an expert Python software engineer building ReconX Enterprise v2.0,
an enterprise-grade vulnerability scanning platform.

CRITICAL REQUIREMENTS:
1. ALL code must have 100% type hints (no Any except justified in docstring)
2. ALL functions/classes must have comprehensive docstrings (Google style)
3. Code must pass: mypy --strict, black, flake8, isort without modifications
4. Minimum 90% test coverage required for all code
5. Follow PEP 484 for type hints, PEP 257 for docstrings, PEP 8 for style
6. Use async/await for I/O operations (database, API calls, file I/O)
7. SQLAlchemy models use BaseModel pattern with relationship() definitions
8. Pydantic schemas for API request/response validation
9. Pytest fixtures for test setup, parametrized tests for edge cases
10. FastAPI routes with proper HTTP status codes and error handling

CODE QUALITY GATE (must pass before commit):
- mypy backend/ --strict → No errors
- black backend/ --check → No changes needed
- flake8 backend/ → No violations
- isort backend/ --check-only → No changes needed
- pytest backend/tests/ --cov=backend --cov-fail-under=90 → 90%+ coverage

When generating code:
- Ask clarifying questions if requirements are ambiguous
- Provide complete, production-ready code (not snippets)
- Include all imports at top of file
- Add setup/teardown for tests
- Use environment variables for configuration
- Include error handling and logging
- Explain architectural decisions in docstrings

IMPORTANT: Never omit code sections. Generate the ENTIRE file/function.
```

---

## 📂 File Organization for Claude

When Claude generates code, it will reference these file paths:

```
reconx-enterprise/
├── backend/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Configuration (pydantic BaseSettings)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base, engine setup
│   │   ├── models.py              # 25 SQLAlchemy models
│   │   ├── session.py             # Database session management
│   │   └── migrations/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # FastAPI dependency injection
│   │   ├── auth.py                # JWT authentication, RBAC
│   │   ├── schemas.py             # Pydantic request/response models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── scans.py           # Scan endpoints
│   │       ├── vulnerabilities.py # Vulnerability endpoints
│   │       ├── reports.py         # Report endpoints
│   │       ├── assets.py          # Asset management
│   │       └── health.py          # Health check endpoint
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── base.py                # ScannerInterface abstract base
│   │   ├── coordinator.py         # ScanOrchestrator main coordinator
│   │   ├── discovery.py           # DiscoveryScanner implementation
│   │   ├── portscan.py            # PortScanScanner implementation
│   │   ├── content.py             # ContentScanner implementation
│   │   ├── vulnscan.py            # VulnerabilityScanScanner implementation
│   │   └── state.py               # StateManager for scan state
│   ├── intelligence/
│   │   ├── __init__.py
│   │   ├── risk_scorer.py         # RiskScoringEngine (CVSS, weighting)
│   │   ├── threat_intel.py        # ThreatIntelligence API client
│   │   ├── compliance_checker.py  # ComplianceChecker (PCI-DSS, HIPAA, etc)
│   │   ├── dependency_mapper.py   # DependencyMapper (tech graph)
│   │   └── cache.py               # Redis caching utilities
│   ├── tasks/
│   │   ├── __init__.py
│   │   └── scan_tasks.py          # Celery tasks for async scanning
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py              # Structured logging
│   │   ├── validators.py          # Input validation helpers
│   │   └── exceptions.py          # Custom exception classes
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py            # Pytest fixtures
│       ├── test_models.py         # Database model tests
│       ├── test_orchestrator.py   # Orchestrator tests
│       ├── test_intelligence.py   # Intelligence module tests
│       ├── test_api.py            # API endpoint tests
│       ├── test_integration.py    # E2E integration tests
│       └── test_performance.py    # Performance/load tests
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   └── tests/
├── deployment/
│   ├── docker/
│   │   ├── Dockerfile.api
│   │   ├── Dockerfile.worker
│   │   └── Dockerfile.frontend
│   ├── kubernetes/
│   │   ├── api-deployment.yaml
│   │   ├── worker-deployment.yaml
│   │   ├── database-statefulset.yaml
│   │   └── kustomization.yaml
│   └── terraform/
├── docs/
├── prompts-design/
├── requirements.txt
├── setup.sh
├── Makefile
└── docker-compose.yml
```

---

## 🔄 Workflow: Claude → File → Verify

### Step 1: Get Code from Claude

```
You (paste prompt from COMPLETE_SEQUENTIAL_PROMPTS.md):
[PROMPT 3.1 FULL TEXT HERE]

Claude will respond with:
- Full file contents
- Explanation of design decisions
- Next prompt to move to
```

### Step 2: Save Code to Right File

```bash
# Claude generates backend/db/models.py
# You copy the code and save to: backend/db/models.py

# Claude generates test file test_models.py
# You copy and save to: backend/tests/test_models.py
```

### Step 3: Run Verification

```bash
# For Python files:
mypy <file> --strict              # Type checking
black <file> --check              # Code format
flake8 <file>                     # Linting
isort <file> --check-only         # Import sorting

# For tests with coverage:
pytest <test_file> -v --tb=short
pytest backend/ --cov=backend --cov-report=html

# For the entire module once complete:
make quality                      # Runs all quality gates
make test                         # Runs full test suite
```

### Step 4: On Success

```
✅ All quality gates passed
✅ Tests passing with 90%+ coverage
✅ Code follows all constraints

→ Move to next prompt (e.g., PROMPT 3.2)
```

### Step 5: On Failure

See [error-recovery.md](error-recovery.md) for detailed troubleshooting.

---

## 💡 Best Practices When Using Claude

### 1. **Copy Complete Prompts**
- Don't summarize
- Include all sections: TASK, REQUIREMENTS, ACCEPTANCE CRITERIA
- Keep the structure intact

### 2. **Provide Context When Needed**
- If Claude asks "What should X return?", provide the specification from COMPLETE_SEQUENTIAL_PROMPTS.md
- Reference section headers in context files for extra details
- Paste package names/versions from requirements.txt if asked

### 3. **Ask for Explanations**
- It's OK to ask Claude: "Explain the type hints for this function"
- Request architecture diagrams if learning new systems
- Ask for implementation alternatives if unsure

### 4. **Handle Long Responses**
- Claude might split code across multiple messages
- Collect all parts before saving to file
- Verify imports at top of file are complete

### 5. **Iterate When Needed**
- If code fails type checking, show Claude the error: "mypy says: [error message]"
- Claude will fix and regenerate
- This is much faster than manual debugging

---

## 📊 Prompt Types in COMPLETE_SEQUENTIAL_PROMPTS.md

### Type 1: CREATE CODE
```
TASK: Create the ScanRun model
REQUIREMENTS:
  - SQLAlchemy ORM model
  - Fields: id, domain, status, started_at, completed_at
  - Relationships: one-to-many with Subdomain
  - Indexes on: status, created_at
  
ACCEPTANCE CRITERIA:
  ✅ Model inherits from Base
  ✅ All fields have type hints
  ✅ Docstring explains purpose
  ✅ Relationships properly defined
```
**What Claude does:** Generates complete model class with docstrings

### Type 2: WRITE TESTS
```
TASK: Test the ScanRun model
REQUIREMENTS:
  - Test model instantiation
  - Test relationships
  - Test index constraints
  - Parametrized tests for edge cases
  
ACCEPTANCE CRITERIA:
  ✅ 90%+ code coverage
  ✅ Edge cases tested
```
**What Claude does:** Generates complete test suite with fixtures

### Type 3: IMPLEMENT FEATURE
```
TASK: Implement RiskScoringEngine
REQUIREMENTS:
  - Class with calculate_risk() method
  - CVSS v3.1 normalization
  - Custom weighting algorithm
  - Caching with Redis
  
ACCEPTANCE CRITERIA:
  ✅ All paths tested
  ✅ Performance: <100ms per calculation
```
**What Claude does:** Generates feature with error handling, logging, tests

### Type 4: INTEGRATION
```
TASK: Integrate RiskScorer into ScanOrchestrator
REQUIREMENTS:
  - Call risk_scorer.calculate_risk() after vulnscan
  - Save results to RiskScore model
  - Log calculation details
  
ACCEPTANCE CRITERIA:
  ✅ Integration tests pass
  ✅ End-to-end scan workflow works
```
**What Claude does:** Modifies existing code, adds integration points

---

## 🔐 Strictness Levels (What Claude Enforces)

### CRITICAL (never skip):
- ✅ Type hints on all functions/params/returns
- ✅ Docstrings for all classes/functions
- ✅ 90%+ test coverage minimum
- ✅ No hardcoded values (use config/env)
- ✅ Async/await for I/O operations
- ✅ Proper error handling with logging

### IMPORTANT (almost never skip):
- ✅ Pydantic dataclass validation for inputs
- ✅ Database transactions for multi-record operations
- ✅ Index on all frequently queried columns
- ✅ Relationship back_populates for bidirectional links
- ✅ FastAPI dependency injection for shared resources

### STRONGLY RECOMMENDED:
- ✅ Comprehensive docstrings with examples
- ✅ Custom exceptions for domain errors
- ✅ Structured logging with context
- ✅ Performance comments for complex logic
- ✅ Separate fixtures for different test scenarios

---

## 🚀 Execution Timeline

| Week | Prompts | Tasks | Est. Hours |
|------|---------|-------|-----------|
| 1-2  | 1.1-1.3 | Verification, setup review | 0.5 |
| 3-4  | 3.1-3.10| Create 25 database models + tests | 40 |
| 5-6  | 5.1-5.10| Orchestrator + scanners + tests | 40 |
| 7-8  | 7.1-7.10| Risk scoring, threat intel | 30 |
| 9-10 | 9.1-9.10| Compliance, dependencies | 30 |
| 11-12| 11.1-11.7| REST API + auth + tests | 35 |
| 13-14| 13.1-13.7| React frontend components | 40 |
| 15-16| 15.1-15.7| Testing, deployment, security | 30 |
| **TOTAL** | **160+ prompts** | **Complete v2.0** | **245 hours** |

---

## 📝 Claude Tips & Tricks

### Tip 1: Context Window Management
- For large functions, Claude can generate in parts
- Ask: "Generate just the __init__ method first"
- Then: "Now generate the calculate_risk method"
- Finally: "Now generate tests for RiskScoringEngine"

### Tip 2: Conflict Resolution
- If Claude generates conflicting signatures with earlier code
- Show it the earlier file: "Here's backend/db/models.py with ScanRun..."
- It will auto-adjust to match existing code patterns

### Tip 3: Rapid Iteration
- For failed tests: "pytest says: [error]. Fix the implementation."
- Claude sees the error and fixes immediately
- Usually correct on second attempt

### Tip 4: Multiple Files at Once
- You can ask for multiple related files in one prompt
- Example: "Generate the RiskScoringEngine class AND its test suite"
- Faster than sequential prompts when they're tightly coupled

### Tip 5: Code Review
- Ask Claude to review its own code: "Review the type hints in RiskScoringEngine"
- Ask for security review: "Check for SQL injection vulnerabilities"
- Catches issues before quality gates

---

## ❌ Common Mistakes to Avoid

### ❌ Mistake 1: Incomplete Prompts
```
WRONG: "Make a model"
RIGHT: [Full prompt from COMPLETE_SEQUENTIAL_PROMPTS.md]
```

### ❌ Mistake 2: Poor Context
```
WRONG: Claude: "What's a ScanRun?"
You: "It's a scan"
RIGHT: You: "ScanRun is the parent record for each security scan, 
       with fields: id, domain, status, started_at. 
       See backend/db/models.py for full definition."
```

### ❌ Mistake 3: Skipping Quality Gates
```
WRONG: Generated code → Save → Next prompt
RIGHT: Generated code → Save → mypy → black → flake8 → pytest → Next prompt
```

### ❌ Mistake 4: Vague Errors
```
WRONG: "This doesn't work"
RIGHT: "mypy says: 'missing return type annotation on line 42 in calculate_risk()'"
```

### ❌ Mistake 5: Missing Dependencies
```
WRONG: Ask Claude to generate code using package not in requirements.txt
RIGHT: Check [requirements.txt](requirements.txt) first, or ask Claude to add dependency
```

---

## 🎓 Learning Path

**If new to Python/async/SQLAlchemy:**
1. Read [SYSTEM_PROMPTS.md](prompts-design/SYSTEM_PROMPTS.md) sections 1-3
2. Complete PROMPT 3.1 (ScanRun model) and study Claude's output
3. Read Claude's docstrings and type hints
4. Ask Claude to explain: "Explain the type hints in ScanRun"
5. Complete all database prompts (3.1-3.10) before moving on

**If experienced but new to this project:**
1. Read [Architecture Decisions](docs/ARCHITECTURE_DECISIONS.md)
2. Read [Weekly Context - Week 3-4](prompts-design/week-3-week-4-context.md)
3. Start with PROMPT 3.1
4. Move through prompts sequentially

**If familiar with codebase:**
1. Start with PROMPT that shows your current weekly context
2. Run quick verification: `make quality && make test`
3. Jump into next incomplete prompt
4. Maintain quality standards throughout

---

## 📞 When to Ask Claude Questions

### Always Ask:
- "Does this design handle [edge case]?"
- "Show me the full file for [filename]"
- "What tests should cover this code?"
- "Explain the type annotation for [function]"

### Sometimes Ask:
- "Any performance concerns with [approach]?"
- "How would we scale this for [scenario]?"
- "What security issues might this have?"

### Don't Ask:
- "Is this good code?" ← Too subjective
- "Should we use [other library]?" ← Beyond current prompt scope
- "How does [unrelated project] work?" ← Off-topic

---

## ✅ Success Checklist

Before moving to next prompt:
- [ ] Code generated and saved to correct file
- [ ] `mypy --strict` passes with 0 errors
- [ ] `black --check` requires no changes
- [ ] `flake8` shows 0 violations
- [ ] `isort --check-only` requires no changes
- [ ] `pytest --cov=backend --cov-fail-under=90` passes with 90%+ coverage
- [ ] All docstrings present and meaningful
- [ ] No `Any` types except justified in docstring
- [ ] Tests cover happy path, edge cases, error cases
- [ ] No hardcoded values (config/env variables used)
- [ ] Async/await used appropriately for I/O
- [ ] README updated if new modules created
- [ ] Git commit made with clear message

---

## 🚨 Emergency: Code Won't Work

See [error-recovery.md](error-recovery.md) for detailed troubleshooting guide.

Quick version:
1. Read the error message carefully
2. Identify the file and line number
3. Show Claude the exact error
4. Claude fixes and regenerates
5. Paste fixed code back
6. Rerun quality gates
7. If still broken → error-recovery.md has deeper solutions

---

## 📚 Related Files

- [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md) - All 160+ prompts
- [restrictions.md](restrictions.md) - Hard constraints Claude must follow
- [context-management.md](context-management.md) - Managing multi-prompt context
- [verification-checklist.md](verification-checklist.md) - Quality verification steps
- [error-recovery.md](error-recovery.md) - Troubleshooting failed code generation
- [SYSTEM_PROMPTS.md](prompts-design/SYSTEM_PROMPTS.md) - Original system design

---

**Ready to start? Open [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md) and begin with PROMPT 3.1!** 🚀
