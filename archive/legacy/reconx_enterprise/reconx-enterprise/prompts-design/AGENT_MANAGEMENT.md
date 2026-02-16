# Agent Management & Orchestration
## How to Coordinate Multiple AI Assistants

---

## 🎯 Overview

You can run **4-5 AI agents in parallel**, each working on different tasks.

**The key:** Clear boundaries, no overlap, synchronized commits.

---

## 👥 Agent Roles & Tools

### Agent 1: Code Generator
**Tool:** Cursor IDE  
**Specialty:** Generate entire files, complex logic  
**Best For:** Database models, API endpoints, core business logic  
**Speed:** 5-15 minutes per file (including fixes)

**Command:**
```
Cursor → Cmd+K → Paste prompt → Get code → Copy to file
```

**When to Use:**
- Creating new `.py` files
- Implementing multiple functions at once
- Complex algorithms
- Models with relationships

**When NOT to Use:**
- One-line fixes (use Copilot instead)
- Quick refactoring (use Copilot instead)
- Explaining code (use Claude instead)

---

### Agent 2: Auto-Complete Assistant
**Tool:** VS Code Copilot  
**Specialty:** Quick suggestions, refactoring, one-liners  
**Best For:** Small additions, fixing typos, completing patterns  
**Speed:** 1-5 minutes per suggestion

**Command:**
```
VS Code → Start typing → Accept suggestion (Tab)
Or: Cmd+I for inline chat
```

**When to Use:**
- Completing repetitive patterns
- Quick bug fixes
- Adding similar functions
- Boilerplate completion

**When NOT to Use:**
- Creating entire new files (too slow)
- Complex logic design (no reasoning)
- Understanding what to do (use Claude instead)

---

### Agent 3: Architecture & Strategy
**Tool:** Claude (Web or Code)  
**Specialty:** Complex reasoning, spanning multiple files  
**Best For:** System design, test strategies, API structures, debugging  
**Speed:** 10-30 minutes per complex task

**Command:**
```
Claude → New chat → Paste SYSTEM_PROMPTS + context → Ask question
```

**When to Use:**
- Designing features spanning multiple files
- Creating comprehensive test suites
- Debugging complex issues
- Architecture decisions
- Reviewing code quality

**When NOT to Use:**
- Quick one-off code generation (too slow)
- Repetitive coding (overkill)
- Simple fixes (use Copilot instead)

---

### Agent 4: Documentation & QA
**Tool:** ChatGPT (Web) or Claude  
**Specialty:** Documentation, explanations, quality review  
**Best For:** Documentation, design docs, code review, creating examples  
**Speed:** 10-20 minutes per document

**Command:**
```
ChatGPT → New chat → Paste code and ask for docs
```

**When to Use:**
- Writing comprehensive documentation
- Creating example usage
- Explaining complex features
- Reviewing work quality
- Creating architecture diagrams

**When NOT to Use:**
- Code generation (gets repetitive)
- Complex logic (misses nuances)

---

### Agent 5: Testing & Validation (OPTIONAL)
**Tool:** Claude or Cursor  
**Specialty:** Test cases, ensuring coverage  
**Best For:** Test files, test strategy, edge cases  
**Speed:** 10-25 minutes per test suite

**Command:**
```
Cursor → Cmd+K → "Create comprehensive tests for this code"
```

**When to Use:**
- Creating test files
- Designing test strategy
- Finding edge cases
- Ensuring coverage

**When NOT to Use:**
- Running existing tests (use make test)
- Quick fixes (use Copilot)

---

## 🔄 Typical Workflow

### Sequential Workflow (Safe, Slower)
```
Monday 9:00 AM  → Agent 1 creates models.py
Monday 10:00 AM → Agent 2 refinement/fixes
Monday 11:00 AM → Agent 3 creates schemas.py
Monday 12:00 PM → Agent 4 creates tests
Monday 1:00 PM  → All tests run & pass
Total: 4 hours for atomic task
```

### Parallel Workflow (Fast, Needs Management)
```
Monday 9:00 AM:
  - Agent 1 (Cursor): Creating models.py
  - Agent 2 (VS Code): Refining existing code
  - Agent 3 (Claude): Designing test strategy
  - Agent 4 (ChatGPT): Documenting architecture

Monday 10:30 AM:
  - Models done ✅
  - Ready for Agent 3 to create tests with models as reference
  - Agent 4 adds to docs
  
Monday 11:00 AM:
  - All done ✅
  - Single commit with all outputs
  
Total: 2 hours for same work!
```

---

## 🚦 Communication Protocol

### Before You Start
```
✅ DO:
1. Tell each agent what others are working on
2. Show each agent the overall structure
3. Define clear file boundaries

❌ DON'T:
1. Let agents edit same file simultaneously
2. Start without clear scope
3. Hope agents "figure it out"
```

### Example: Multi-Agent Task Breakdown

**Goal:** Build complete domain scanning module

**Agent 1 (Cursor):**
```
TASK: Create models.py with Domain + DomainScan models
FILES TO CREATE: backend/db/models.py (add to existing)
SCOPE: ONLY the two model classes, relationships, docstrings
DO NOT: Modify any other files
WHAT OTHERS ARE DOING:
  - Agent 2: Creating test file
  - Agent 3: Creating API endpoint
  - Agent 4: Writing documentation
```

**Agent 2 (VS Code):**
```
TASK: Create test suite for domain models
FILES TO CREATE: backend/tests/test_domain_models.py
SCOPE: Unit tests ONLY for the two model classes
DO NOT: Create any new code files
DEPENDS ON: Agent 1 must finish first (you need the model definitions)
WHAT OTHERS ARE DOING:
  - Agent 1: Creating models (you'll wait for this)
  - Agent 3: Creating API endpoint
  - Agent 4: Writing documentation
```

**Agent 3 (Claude):**
```
TASK: Design API endpoint structure for domain scans
FILES TO CREATE: backend/api/routes/domains.py
SCOPE: Endpoints for CRUD operations on scans
DO NOT: Implement database operations (Agent 1 handles models)
DEPENDS ON: Agent 1 (needs to know model structure)
SCHEDULING: Can start after Agent 1 defines models
WHAT OTHERS ARE DOING:
  - Agent 1: Creating models
  - Agent 2: Creating tests (can wait for models)
  - Agent 4: Writing documentation
```

**Agent 4 (ChatGPT):**
```
TASK: Create API documentation
FILES TO CREATE: docs/API_DOMAIN_SCANS.md
SCOPE: Document the endpoints that Agent 3 is creating
DO NOT: Create code files
CAN WORK: In parallel with others (based on requirements, not final code)
WHAT OTHERS ARE DOING:
  - Agent 1: Creating models
  - Agent 2: Creating tests
  - Agent 3: Creating endpoints
```

---

## 🤝 Agent Handoff Protocol

### Step 1: Define Clear Interfaces

**Agent 1 (Cursor) creates:**
```python
# backend/db/models.py

class Domain(Base):
    """Represents a scanned domain."""
    __tablename__ = "domains"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    scans = relationship("DomainScan", back_populates="domain")

class DomainScan(Base):
    """Represents a scan of a domain."""
    __tablename__ = "domain_scans"
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    domain = relationship("Domain", back_populates="scans")
    status = Column(String(50), default="pending")
```

**Passes to Agents 2, 3, 4:**
```
From Agent 1:
"Models created in backend/db/models.py

Available classes:
- Domain(id, name, scans)
- DomainScan(id, domain_id, domain, status)

You can import with:
from backend.db.models import Domain, DomainScan"
```

### Step 2: Agent 2 Uses the Interface

**Agent 2 (VS Code) in test file:**
```python
from backend.db.models import Domain, DomainScan

def test_domain_creation():
    domain = Domain(name="example.com")
    assert domain.name == "example.com"
```

### Step 3: Agent 3 Uses the Interface

**Agent 3 (Claude) in API routes:**
```python
from backend.db.models import Domain, DomainScan
from sqlalchemy.orm import Session

@router.post("/domains/{domain_id}/scan")
async def create_scan(domain_id: int, db: Session):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(404, "Domain not found")
    scan = DomainScan(domain_id=domain_id, status="pending")
```

### Step 4: Agent 4 Documents It

**Agent 4 (ChatGPT) adds to docs:**
```
## Domain Scanning API

### Models
- Domain: Represents a scanned domain
- DomainScan: Represents one scan of a domain

### Endpoints
- POST /domains/{domain_id}/scan - Create new scan
- GET /domains/{domain_id}/scans - List scans
```

---

## 🎯 Sample 1-Week Plan with Agents

### Monday (Start Together)
**All agents read:**
- week-3/CONTEXT.md
- week-3/PROMPTS.md
- Understand what's being built

**Assignment:**
```
Agent 1: Database Layer (models.py)
Agent 2: Test Suite (test_models.py)
Agent 3: API Layer (routes/scans.py)
Agent 4: Documentation (API_REFERENCE.md)
```

### Monday 9:00 - 10:00 AM

**Agent 1 (Cursor):**
```
Prompt: week-3/PROMPTS.md → "Create ScanRun model"
Output: backend/db/models.py with ScanRun class ✅
```

**Agent 2 (VS Code):**
```
Waiting... Can't test something that doesn't exist yet
Use this time to: Review test strategy, set up conftest.py
```

**Agent 3 (Claude):**
```
Working on: Design requirements for API
Output: Pydantic schemas (not yet tied to models)
```

**Agent 4 (ChatGPT):**
```
Working on: User guide for scanning workflow
Output: Draft documentation
```

### Monday 10:00 - 11:00 AM

**Agent 1:** ✅ Done, waiting

**Agent 2 (VS Code):**
```
Now that models exist...
From Agent 1: "ScanRun model created with fields: id, domain, status, created_at"
Prompt: week-3/PROMPTS.md → "Create tests for ScanRun model"
Output: backend/tests/test_models.py with ScanRun tests ✅
```

**Agent 3 (Claude):**
```
Now that models exist...
From Agent 1: "ScanRun model fields..."
Prompt: week-3/PROMPTS.md → "Create POST /scans endpoint"
Output: API endpoint that uses ScanRun model ✅
```

**Agent 4:** Still documenting

### Monday 11:00 AM - 12:00 PM

**All agents:**
```
Review each other's work
Test: make test (all pass?)
Fix any issues
```

**Agent 4 (ChatGPT):**
```
Now that code exists...
From others: Models, tests, API endpoints
Prompt: "Create comprehensive API documentation from this code"
Output: Complete API_REFERENCE.md ✅
```

### Monday 12:00 PM

**You (Human):**
```
Review all four outputs
make test → All pass? ✅
make lint → All formatted? ✅
git commit -m "feat: add ScanRun model with tests, API, documentation"
Ready for Tuesday tasks!
```

**Time invested: 3 hours (parallel work)**

---

## ⚠️ Common Pitfalls & Solutions

### Pitfall 1: Agent Collision
**Problem:** Two agents edit same file simultaneously

**Solution:**
```
❌ WRONG:
Agent 1: "Edit backend/db/models.py"
Agent 2: "Edit backend/db/models.py"

✅ CORRECT:
Agent 1: "Create backend/db/models.py with models A, B"
Agent 2: "Create backend/db/schemas.py with schemas A, B"
Or: Agent 2 works on different file: backend/tests/test_models.py
```

### Pitfall 2: Missing Dependencies
**Problem:** Agent 3 needs output from Agent 1, but Agent 1 isn't done

**Solution:**
```
Create dependency tree:

Agent 1 (models) ← Foundation
  ↓
Agent 2 (tests) ← Needs models
Agent 3 (API) ← Needs models
Agent 4 (docs) ← Needs everything else

Execution order:
1. Agent 1 completes
2. Agents 2, 3, 4 start in parallel (all need Agent 1's output)
```

### Pitfall 3: Scope Creep
**Problem:** Agent starts doing more than assigned

**Solution:**
```
Tell agent explicitly:

✅ CORRECT:
"Create ONLY the ScanRun model, nothing else.
INCLUDE: 5 fields, docstrings, type hints
EXCLUDE: Tests, API routes, relationships"

❌ WRONG:
"Create the database layer" ← Too vague, agent adds everything
```

### Pitfall 4: Context Loss
**Problem:** Agent doesn't know about project conventions

**Solution:**
```
Always include preamble:

-----
[SYSTEM_PROMPTS.md content]
[Week context]
[Project structure excerpt]
-----
[Specific task]
```

### Pitfall 5: Quality Degradation
**Problem:** Multiple agents = inconsistent code style

**Solution:**
```
Every agent must include in its prompt:

"Follow SYSTEM_PROMPTS.md requirements:
- Type hints on all functions
- Google-style docstrings
- PEP 8 formatting (black 88-char lines)
- Tests for all public functions"

Then:
make lint  # Runs black, flake8, isort
make test  # Ensures tests pass
```

---

## 🔧 Agent Coordination Tools

### Tool 1: Shared Progress Document

**Create:** `prompts-design/AGENT_PROGRESS.md`

```markdown
## Monday, Week 3

### Agent 1 (Cursor) - Code Generation
- ✅ 9:00 AM: ScanRun model created
- ✅ 10:30 AM: Subdomain model created
- ⏳ 11:00 AM: Working on API integration
- ⏹️ 12:00 PM: Done for today

### Agent 2 (VS Code) - Testing
- ⏳ 9:00 AM: Waiting for models
- ✅ 10:30 AM: Started writing tests
- ✅ 11:30 AM: Test suite complete
- ⏹️ 12:00 PM: Done for today

### Agent 3 (Claude) - Architecture
- ✅ 9:00 AM: Designed API routes
- ✅ 10:00 AM: Started implementation
- ⏳ 11:00 AM: Waiting for models
- ✅ 11:45 AM: Complete
- ⏹️ 12:00 PM: Done for today

### Dependencies
- ✅ Agent 1 → Agent 2 (models for tests)
- ✅ Agent 1 → Agent 3 (models for API)
- ⏳ All → Agent 4 (documentation waits)
```

### Tool 2: Task Interface Definition

**Create:** `prompts-design/TASK_INTERFACES.md`

```markdown
## Task: ScanRun Model

### Agent 1 Output (Cursor)
Files: backend/db/models.py
Classes: ScanRun
Fields: id, domain, status, created_at, scan_type
Methods: __repr__(), __dict__()

### Agent 2 Input (VS Code depends on Agent 1)
Can import: from backend.db.models import ScanRun
Test against: ScanRun.query, ScanRun.id, ScanRun.domain

### Agent 3 Input (Claude depends on Agent 1)
Can import: from backend.db.models import ScanRun
Use in: FastAPI models, DB queries

### Agent 4 Input (ChatGPT depends on all)
Documents: All APIs, all models, all flows
```

### Tool 3: Git Branching Strategy

**For parallel agents:**
```bash
# Main development
git checkout -b week-3-features

# Each agent gets sub-branch (optional, if working truly parallel)
git checkout -b week-3-models         # Agent 1
git checkout -b week-3-tests          # Agent 2
git checkout -b week-3-api            # Agent 3
git checkout -b week-3-docs           # Agent 4

# After each agent finishes
git commit -m "feat: add ScanRun model"
git push origin week-3-models

# Human merges
git checkout week-3-features
git merge week-3-models week-3-tests week-3-api week-3-docs
```

**Simpler approach:** All agents commit to same `week-3-features` branch

---

## 📊 Efficiency Metrics

### Track Per Agent

**Agent 1 (Code Generation):**
- Tasks completed: ___
- Avg time per task: ___ min
- % requiring fixes: ___%
- Accuracy: ___%

**Agent 2 (Auto-completion):**
- Tasks completed: ___
- Avg time per task: ___ min
- % requiring fixes: ___%

**Agent 3 (Architecture):**
- Tasks completed: ___
- Avg time per task: ___ min
- % requiring fixes: ___%

**Agent 4 (Documentation):**
- Tasks completed: ___
- Avg time per task: ___ min
- Quality rating: __/5

### Success Criteria

✅ All agents complete assigned tasks  
✅ 0 merge conflicts  
✅ All tests pass 100%  
✅ 85%+ coverage maintained  
✅ Code review approved  
✅ Single clean commit per day  

---

## 🎓 Agent Best Practices

### ✅ DO

1. **Clear scope** - Tell agents exactly what to do
2. **Provide context** - Include relevant files, structure
3. **Include examples** - Show what success looks like
4. **Verify independently** - You run tests, not agent
5. **Commit frequently** - After each subtask
6. **Document decisions** - Why this approach?

### ❌ DON'T

1. **Mega-prompts** - Don't ask agent to do 10 things
2. **Assume understanding** - Be explicit
3. **Skip quality gates** - Always run tests
4. **Mix overlapping tasks** - Clear boundaries
5. **Expect perfection** - Review and refine
6. **Skip documentation** - Future you will thank current you

---

## 🚀 Starting Multiple Agents

### Setup (5 minutes)

```bash
# Terminal 1: VS Code Copilot (already in VS Code)
# Just start typing in a file

# Terminal 2: Open Cursor IDE
cursor .

# Terminal 3: Open Claude Web
# https://claude.ai

# Terminal 4: Optional - keep for testing
# make test
```

### Assignment (5 minutes)

```
Print or screenshot this template:

AGENT 1 (Cursor IDE):
Task: ________________
Files: ________________
Output: ________________
DON'T: ________________

AGENT 2 (VS Code):
Task: ________________
Files: ________________
Depends on: ________________
DON'T: ________________

[etc for each agent]
```

### Execution (Variable)

```
1. Give each agent their snippet
2. They execute simultaneously
3. You monitor progress
4. Merge when all done
5. Run tests
6. Commit
```

---

## 📞 Escalation: When Agents Struggle

### Problem: Agent keeps generating wrong code

**Solution:**
```
1. Tell agent the problem clearly
2. Provide corrected example
3. Ask: "Can you regenerate with these specifics?"
4. If fails again: Try different agent
   - Cursor → Claude
   - Claude → Cursor
   - Either → ChatGPT
```

### Problem: Agent doesn't understand requirements

**Solution:**
```
1. Simplify language (more specific)
2. Provide example of expected output
3. Add constraints ("Must include X, can't do Y")
4. Try breaking into smaller subtasks
```

### Problem: Agents create conflicting code

**Solution:**
```
1. STOP and merge manually
2. Keep one version
3. Delete the other
4. Update TASK_INTERFACES.md to prevent
5. Clearly assign one agent per file
```

---

## 🎬 Sample Full Day

**Morning:**
```
9:00 AM:  All agents read CONTEXT.md + PROMPTS.md
9:15 AM:  You assign 4 tasks to 4 agents
9:20 AM:  Agent 1 starts (Cursor)
9:25 AM:  Agent 2 starts (VS Code)
9:30 AM:  Agent 3 starts (Claude)
9:35 AM:  Agent 4 starts (ChatGPT)
```

**Midday:**
```
11:00 AM: Agent 1 ✅ done
11:15 AM: Agent 2 ✅ done (was waiting for Agent 1)
11:30 AM: Agent 3 ✅ done
11:45 AM: Agent 4 ✅ done
```

**Afternoon:**
```
12:00 PM: You review all outputs (15 min)
12:15 PM: You run: make lint (2 min)
12:17 PM: You run: make test (5 min)
12:22 PM: All green ✅
12:23 PM: git commit (1 min)
12:24 PM: Next day's assignment ready
```

**Total real-time:** 3.5 hours  
**Work completed:** 4 atomic tasks  
**If done sequentially:** 8+ hours  

**5x FASTER with parallel agents!**

---

## Summary

- **1 Agent:** Sequential, slow, safe
- **2-3 Agents:** Much faster, requires clear scoping
- **4+ Agents:** 5x faster, needs careful choreography
- **Key rule:** Clear boundaries, no overlap
- **Result:** Week's work in 2 days, while maintaining quality

Now you're ready to orchestrate your AI team! 🚀
