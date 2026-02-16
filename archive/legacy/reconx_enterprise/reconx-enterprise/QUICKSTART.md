# 🎯 Claude Agent Quickstart Guide

**Purpose:** Fast reference for getting started with Claude code generation for ReconX Enterprise

**Read this first** if you just want to get working without detailed explanations.

---

## ⚡ 60-Second Setup

```bash
# 1. Navigate to project
cd /path/to/reconx-enterprise

# 2. Verify environment
docker-compose ps      # Should show 8 services "Up"
make quality          # Should pass (already set up)

# 3. You're ready!
```

---

## 🎯 5-Step Workflow for Each Prompt

```
1. OPEN
   └─ COMPLETE_SEQUENTIAL_PROMPTS.md
   └─ Find your current prompt (e.g., PROMPT 3.1)

2. COPY
   └─ Copy complete prompt text

3. SEND TO CLAUDE
   └─ Paste prompt to Claude
   └─ Include system message first time only (see below)

4. SAVE CODE
   └─ Copy generated code
   └─ Save to file path specified in prompt
   └─ Example: backend/db/models.py

5. VERIFY
   └─ Run: mypy <file> --strict
   └─ Run: make quality && make test
   └─ If passes ✅ → Next prompt
   └─ If fails ❌ → See error-recovery.md
```

---

## 📋 System Message (Copy-Paste Once)

**FIRST TIME ONLY:** Paste this to Claude as system message before your first prompt:

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

After this, just paste prompts normally—Claude will remember these requirements.

---

## 📂 Key Files Reference

| File | Purpose | Read When |
|------|---------|-----------|
| [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md) | All 160+ prompts in order | Every prompt session |
| [claude.md](claude.md) | Detailed guide for Claude workflows | Setting up or workflow questions |
| [restrictions.md](restrictions.md) | Hard constraints and rules | Understanding why certain code required |
| [error-recovery.md](error-recovery.md) | Fix failed code generation | Code fails quality gates |
| [verification-checklist.md](verification-checklist.md) | Quality verification steps | Verifying generated code |
| [context-management.md](context-management.md) | Managing multi-prompt context | When code depends on earlier work |

---

## 🔄 Typical Workflow (Example: PROMPT 3.1)

### Step 1: Find Prompt
```
Open COMPLETE_SEQUENTIAL_PROMPTS.md
Scroll to "PROMPT 3.1: Create ScanRun Model"
```

### Step 2: Copy Prompt Text
```
[Copy everything from TASK: to the end of the prompt block]
```

### Step 3: Paste to Claude
```
Claude, here's the prompt:

[PASTE FULL PROMPT]
```

### Step 4: Get Code & Save
```
Claude generates full ScanRun class with imports and docstrings
You copy the full file content
Save to: backend/db/models.py
```

### Step 5: Verify
```bash
# Type hints
mypy backend/db/models.py --strict
# Should output: Success: no issues found in 1 source file

# Code format
black backend/db/models.py --check
# Should output: All done! ✨ 🍰 ✨ 1 file would be left unchanged.

# Linting
flake8 backend/db/models.py
# Should output: [nothing]

# All at once (recommended)
make quality && make test
# Should output: ✅ All tests passed with 90%+ coverage
```

### Step 6: Move to Next Prompt
```
If all above pass → PROMPT 3.2 ✅
If any fail → See error-recovery.md
```

---

## ⚡ Quick Commands

```bash
# Run all quality gates
make quality

# Run all tests with coverage
make test

# Run tests for specific module
pytest backend/tests/test_models.py -v

# View test coverage HTML report
pytest backend/tests/ --cov=backend --cov-report=html
open htmlcov/index.html  # macOS

# Auto-fix most issues
black backend/
isort backend/
autoflake --in-place --recursive backend/

# Check what's broken
mypy backend/ --strict 2>&1 | head
flake8 backend/ 2>&1 | head
pytest backend/ -x -v  # Stop at first failure
```

---

## ❌ Common Issues & Fixes

### Issue: "missing return type annotation"
**Fix:** Claude will add type hint automatically with system message
**Or:** Tell Claude: `mypy says "missing return type annotation". Add it.`

### Issue: "test coverage below 90%"
**Fix:** Run: `pytest backend --cov=backend --cov-report=html`
Open htmlcov/index.html to see uncovered lines
Tell Claude: `Coverage is 85%, need 90%+. Add tests for lines X-Y.`

### Issue: "ImportError: cannot import name X"
**Fix:** 
1. Check file exists: `ls -la backend/db/models.py`
2. Check class is there: `grep "class X" backend/db/models.py`
3. Check __init__.py exports: `cat backend/db/__init__.py`
4. Or ask Claude: `ImportError importing X. Fix imports.`

### Issue: Code looks wrong but passes tests
**Fix:** Ask Claude for code review: `Review these type hints for correctness: [function]`

---

## 🧠 When to Use Each File

### I just want to work
→ Copy system message → Follow 5-step workflow above → Use quick commands

### Code doesn't pass quality gates
→ See [error-recovery.md](error-recovery.md) for specific error type

### Code fails at integration
→ See [verification-checklist.md](verification-checklist.md) Section "Integration Tests"

### Code depends on earlier files
→ See [context-management.md](context-management.md) for how to share context

### I want detailed workflow explanation
→ Read [claude.md](claude.md)

### I want to understand constraints
→ Read [restrictions.md](restrictions.md)

---

## 📊 Progress Tracking

**To see progress:**

```bash
# See which model files exist
ls -la backend/db/models.py

# See how many test files written
find backend/tests -name "test_*.py" | wc -l

# See test coverage
pytest backend/ --cov=backend --cov-report=term

# See git commits
git log --oneline | head -20
```

**Track in README:**
```markdown
## Progress

- [x] Week 1-2: Foundation (PROMPT 1.1-1.3)
- [x] Week 3-4: Database Models (PROMPT 3.1-3.10)
- [ ] Week 5-6: Orchestrator (PROMPT 5.1-5.10)
- [ ] Week 7-10: Intelligence (PROMPT 7.1-10.10)
- [ ] Week 11-12: API (PROMPT 11.1-11.7)
- [ ] Week 13-14: Frontend (PROMPT 13.1-13.7)
- [ ] Week 15-16: Testing (PROMPT 15.1-15.7)
```

---

## 🚀 Ready to Start?

1. ✅ System message copied
2. ✅ Environment verified (make quality passes)
3. ✅ [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md) opened
4. ✅ Looking at PROMPT 3.1 or your current prompt

**→ Copy prompt → Paste to Claude → Save code → Run make quality → 🎉**

---

## 📞 Need Help?

| Question | Answer |
|----------|--------|
| "How do I use Claude effectively?" | Read [claude.md](claude.md) |
| "Code fails - what do I do?" | See [error-recovery.md](error-recovery.md) |
| "How do I verify the code?" | Use [verification-checklist.md](verification-checklist.md) |
| "What are the constraints?" | Read [restrictions.md](restrictions.md) |
| "Code depends on earlier work?" | See [context-management.md](context-management.md) |
| "Quick reference?" | You're reading it now! |

---

**Made for speed. Quality built-in. Let's build ReconX Enterprise v2.0!** 🚀
