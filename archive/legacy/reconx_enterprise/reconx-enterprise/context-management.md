# 📚 Context Management - Multi-Prompt Workflows

**Purpose:** Manage context effectively when working with Claude across multiple sequential prompts

**Version:** v2.0  
**Scope:** Context window management, dependency tracking, state preservation

---

## 🎯 Context Overview

When using Claude for ReconX Enterprise:

- **Each prompt:** ~3-10 minutes of conversation
- **Claude context window:** 200K tokens (very large)
- **Code to generate:** ~15,000 lines Python + 3,000 lines React over 16 weeks
- **Challenge:** Keeping Claude context-aware as you move through prompts

---

## 🔄 Context Workflow: Multi-Prompt Chain

```
Week 1: Establish system message & baseline
    ↓
Prompt 3.1: Create ScanRun model
    ↓
Prompt 3.2: Create Subdomain model (depends on ScanRun)
    ↓
Prompt 3.3: Create Relationship tests (depends on 3.1, 3.2)
    ↓
... and so on
```

**Key Context Maintenance Strategy:**

For each prompt, Claude needs:
1. **System message** (from [claude.md](claude.md) - once at start)
2. **Current prompt** (from COMPLETE_SEQUENTIAL_PROMPTS.md - every prompt)
3. **Relevant existing code** (when dependencies exist - selective)
4. **Quality gate requirements** (from [restrictions.md](restrictions.md) - once at start)

---

## 🚀 START OF SESSION (First Prompt Only)

### Step 1: Initialize Claude with System Message

On your **very first prompt** to Claude, include this system message:

<**Copy from [claude.md](claude.md) - "System Message for Claude" section**>

This sets expectations for:
- Type hints (100%)
- Docstrings (Google style)
- Test coverage (90%+)
- Quality gates (mypy, black, flake8, isort)
- Architecture patterns

### Step 2: Provide Initial Context

For Prompt 3.1, tell Claude:

```
You're building ReconX Enterprise v2.0 - an enterprise security scanning platform.

Architecture:
- Backend: FastAPI + SQLAlchemy ORM + PostgreSQL
- Database: 25 models with relationships
- Orchestrator: 4-phase scanning (Discovery, PortScan, Content, VulnScan)
- Intelligence: Risk scoring, threat intel, compliance checking
- API: REST endpoints with JWT auth and RBAC
- Frontend: React dashboard with reporting

Current task: Create database models starting with ScanRun

[Paste PROMPT 3.1 here]
```

---

## 📖 MID-SESSION (Prompts 2-159)

### For Each Subsequent Prompt:

**Option 1: Fresh Start (Recommended for clarity)**
```
You (to Claude):
We're continuing the ReconX Enterprise build. Moving to next task.

[Paste PROMPT 3.2 here]
```

Claude has perfect long-term memory and will maintain quality standards.

**Option 2: With Explicit Context (When Dependencies Exist)**

For Prompt 3.2 (creating Subdomain model that depends on ScanRun):

```
You (to Claude):
Next task: Create the Subdomain model.

Context from previous work:
- Completed: ScanRun model in backend/db/models.py
- ScanRun has: id (int), domain (str), status (ScanStatus), timestamps
- Subdomain should have many-to-one relationship with ScanRun

[Paste full ScanRun model code from backend/db/models.py]

Now create Subdomain:
[Paste PROMPT 3.2 here]
```

### When to Use Explicit Context:

✅ **Do include context when:**
- Creating related models (Subdomain depends on ScanRun)
- Implementing features that extend existing code
- Writing tests for integration scenarios
- Adding methods to existing classes

❌ **Don't include context when:**
- Creating standalone modules (DiscoveryScanner doesn't depend on PortScanScanner directly)
- Each function is independent
- Context would make prompt too long

---

## 🧵 Context Dependencies Map

**Which prompts need context from earlier prompts:**

### Database Models (Prompts 3.1-3.10)

```
3.1: ScanRun ↓
               ← 3.2: Subdomain (needs ScanRun)
               ← 3.3: PortScan (needs ScanRun)
               ← 3.4: Vulnerability (needs ScanRun)

3.2, 3.3, 3.4 → 3.5: HTTPHeader (needs PortScan)
             → 3.6: Tests (need all models)
```

**Context to include:**
- 3.2: Show ScanRun model code
- 3.3: Show ScanRun model code
- 3.4: Show ScanRun, PortScan model codes
- 3.5: Show PortScan model code
- Tests: Show all model definitions

### Orchestrator (Prompts 5.1-5.10)

```
5.1: ScannerInterface (base) ↓
                             ← 5.2: DiscoveryScanner (extends base)
                             ← 5.3: PortScanScanner (extends base)
                             ← 5.4: ContentScanner (extends base)
                             ← 5.5: VulnerabilityScanner (extends base)

5.1-5.5 → 5.6: ScanOrchestrator (uses all scanners)
        → 5.7: StateManager
        → 5.8: Tests
```

**Context to include:**
- 5.2-5.5: Show ScannerInterface base class
- 5.6: Show all scanner implementations
- Tests: Show orchestrator + scanner code

### Intelligence (Prompts 7.1-10.10)

```
7.1: RiskScoringEngine ↓
7.2: ThreatIntelligence ↓
7.3: ComplianceChecker ↓
7.4: DependencyMapper ↓
     All mostly independent, but:
     
7.1-7.4 (all engines) → 8.1: Intelligence API router (uses all engines)
                      → 8.2: Integration tests
```

**Context to include:**
- 8.1: Show all 4 engine implementations
- Tests: Show integrated engine code

### API (Prompts 11.1-11.7)

```
11.1: Schemas (Pydantic models) ↓
11.2: Auth (JWT, RBAC) ↓
11.3: Dependencies  ↓
11.4: Routes - Scans (uses 11.1, 11.2, 11.3, models) ↓
11.5: Routes - Vulnerabilities ↓
11.6: Routes - Reports ↓
11.7: Tests
```

**Context to include:**
- 11.4-11.6: Show schemas, auth, models code
- Tests: Show full API code

---

## 💾 How to Share Code with Claude

### Method 1: Paste Code Directly

For small code (<500 lines):
```
You:
Here's the ScanRun model from backend/db/models.py:

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.db.base import Base

class ScanRun(Base):
    __tablename__ = "scan_runs"
    
    id: int = Column(Integer, primary_key=True, index=True)
    domain: str = Column(String(255), nullable=False, index=True)
    ...
```

Now create the Subdomain model with proper relationships:
[Paste PROMPT 3.2]
```

### Method 2: Reference File Path (For Large Code)

For large code (>500 lines):
```
You:
Here's current state of backend/db/models.py:
[Show first 50 lines - the critical parts]
...
[Show last 20 lines]

(Full file has 25 models, shown key sections above)

Now add the Vulnerability model:
[Paste PROMPT 3.4]
```

### Method 3: Summarized Context

When code is very large or complex:
```
You:
Current database models structure:
- ScanRun: Parent scan record (id, domain, status, timestamps)
  Relationships: one-to-many with Subdomain, PortScan, Vulnerability
- Subdomain: Sub-domain discovery (name, domain_id, is_alive)
  Relationships: many-to-one with ScanRun, one-to-many with PortScan
- PortScan: Port scanning results (port, protocol, status, service)
  Relationships: many-to-one with Subdomain

All models inherit from Base and use SQLAlchemy ORM pattern.
All have 100% type hints and comprehensive docstrings.

Create the Vulnerability model next:
[Paste PROMPT 3.4]
```

---

## 🔐 Avoiding Context Loss

### Problem: "Claude doesn't remember earlier work"

**Cause:** You didn't include necessary context in the prompt

**Solution:** Include relevant code explicitly

**Example:**
```
❌ WRONG:
You: Create the Subdomain model tests

(Claude doesn't know what Subdomain looks like or what relationships it has)

✅ CORRECT:
You: Here's the Subdomain model:
[Subdomain code pasted]

Create comprehensive tests for Subdomain including relationship tests:
[Paste PROMPT 3.3]
```

### Problem: "Code style or patterns changed"

**Cause:** Didn't maintain consistent context from earlier work

**Solution:** Show Claude examples from earlier models

**Example:**
```
✅ CORRECT:
Here's the ScanRun model we created (use this as style reference):
[ScanRun code]

Create Subdomain using the SAME patterns:
[Paste PROMPT 3.2]
```

### Problem: "Integration broke after new code"

**Cause:** New code didn't know about existing code dependencies

**Solution:** Include integration context

**Example:**
```
✅ CORRECT:
Here's how ScanRun is used in the orchestrator:
```python
scan = ScanRun(domain="example.com")
subdomains = scan.subdomains  # Relationship access
```

Create Subdomain model maintaining this relationship pattern:
[Paste PROMPT 3.2]
```

---

## 📝 Context Checklist for Each Prompt

Before pasting prompt to Claude:

- [ ] **System message provided** (only first prompt)
- [ ] **Prompt copied exactly** from COMPLETE_SEQUENTIAL_PROMPTS.md
- [ ] **Dependencies identified** - What code does this depend on?
- [ ] **If dependencies exist** - Include relevant existing code
- [ ] **If integration** - Show how it integrates with other modules
- [ ] **Quality requirements** - Remind of quality standards if new developer
- [ ] **File paths correct** - Verify where code should go

---

## 🎓 Examples: Before & After

### Example 1: Database Model Chain

**WRONG approach:**
```
Prompt 1: Create ScanRun
Claude: [generates ScanRun]
You: Save to file

Prompt 2: Create Subdomain
You: [Paste PROMPT 3.2]
Claude: [generates Subdomain, but might not match ScanRun style]
```

**RIGHT approach:**
```
Prompt 1: Create ScanRun
Claude: [generates ScanRun]
You: Save to file ✅

Prompt 2: Create Subdomain
You: Here's ScanRun (for style reference):
[paste ScanRun code]
Now create Subdomain with matching patterns and relationship:
[Paste PROMPT 3.2]
Claude: [generates Subdomain matching ScanRun style] ✅
You: Save to file
```

### Example 2: Feature Implementation

**WRONG approach:**
```
Prompt 1: Create RiskScoringEngine
Claude: [generates]
You: Save

Prompt 2: Integrate RiskScorer into Orchestrator
You: [Paste PROMPT 8.1]
Claude: [tries to integrate but doesn't know RiskScoringEngine signature]
```

**RIGHT approach:**
```
Prompt 1: Create RiskScoringEngine
Claude: [generates]
You: Save to backend/intelligence/risk_scorer.py ✅

Prompt 2: Integrate into Orchestrator
You: Here's the RiskScoringEngine from backend/intelligence/risk_scorer.py:
[show key methods and signatures]

Here's the ScanOrchestrator structure:
[show orchestrator class outline]

Integrate RiskScoringEngine into the orchestrator:
[Paste PROMPT 8.1]
Claude: [generates integration correctly] ✅
```

### Example 3: Test Suite

**WRONG approach:**
```
Prompt 1: Create models
Claude: [generates all 25 models]

Prompt 2: Create model tests
You: [Paste PROMPT 3.6]
Claude: [generates tests, assumes model structure]
```

**RIGHT approach:**
```
Prompt 1: Create models
Claude: [generates ScanRun, Subdomain, PortScan, ...]
You: Save each to backend/db/models.py ✅

Prompt 2: Create model tests
You: Here's our models structure:
[Show first 100 lines of backend/db/models.py - includes ScanRun, Subdomain definitions]

Create comprehensive tests covering:
- Model instantiation
- Field validation
- Relationships
- Constraints

Use pytest patterns with fixtures:
[Paste PROMPT 3.6]
Claude: [generates tests that match actual model structure] ✅
```

---

## 🔄 Context for Troubleshooting

When code fails and you're fixing with Claude:

### Scenario: Test failure

```
Pytest output:
FAILED backend/tests/test_models.py::TestScanRun::test_relationships
AssertionError: assert None == 'example.com'

You tell Claude:
Test fails on line 42 of test_models.py.

Here's the failing test:
```python
def test_relationships(self, db_session):
    scan = ScanRun(domain="example.com")
    db_session.add(scan)
    db_session.commit()
    
    subdomain = Subdomain(scan_id=scan.id, name="sub.example.com")
    db_session.add(subdomain)
    db_session.commit()
    
    assert subdomain.scan_run.domain == "example.com"  # Line 42 - None!
```

Here's the ScanRun model:
```python
class ScanRun(Base):
    __tablename__ = "scan_runs"
    id: int = Column(Integer, primary_key=True)
    domain: str = Column(String(255))
    subdomains: list[Subdomain] = relationship("Subdomain", back_populates="scan_run")

class Subdomain(Base):
    __tablename__ = "subdomains"
    id: int = Column(Integer, primary_key=True)
    scan_id: int = Column(Integer, ForeignKey("scan_runs.id"))
    scan_run: ScanRun = relationship("ScanRun", back_populates="subdomains")
```

Why is subdomain.scan_run None? Fix the test or model.
```

Claude can now fix because it has:
1. Error message
2. Failing test code
3. Model definitions
4. Full context

---

## 🎯 Context Size Guidelines

**Keep single prompt context to:**
- <5,000 tokens of existing code = ~2,000 lines of code
- Includes prompt + system instructions + relevant code

**If context getting too large:**
1. Split into multiple prompts
2. Or reference just the critical parts
3. Tell Claude: "Here's the key type definitions:" (show just signatures, not full implementation)

---

## 💡 Pro Tips

### Tip 1: Save Outputs with Context

```bash
# When Claude generates ScanRun, save with context:
# File: backend/db/models.py
# Section: ScanRun class (lines 1-50)
# Prompt: 3.1 - Create ScanRun Model
# Status: ✅ Passes mypy, black, flake8, isort, 95% coverage

[Claude's generated code here]
```

This makes it easy to find necessary code later.

### Tip 2: Incremental Context Building

Don't paste ALL 25 models when creating model 26. Only paste:
- The base class used by all models
- Most similar model for style reference
- Current model you're extending

### Tip 3: Use Claude's Memory

Claude maintains context within a conversation thread. So:
```
You: Create ScanRun [Paste PROMPT 3.1]
Claude: [generates]

You: Create Subdomain [Paste PROMPT 3.2]
Claude: Remembers ScanRun from earlier in conversation

You: Create tests for both [Paste PROMPT 3.6]
Claude: Remembers both models from earlier
```

You can keep same conversation thread for entire week (3.1-3.10).

### Tip 4: Reference Previous in Same Thread

Within same conversation:
```
You: Create test for ScanRun relationships with the models we created earlier

[Paste PROMPT 3.6]
```

Claude will reference ScanRun, Subdomain, PortScan from earlier in same conversation.

---

## 📊 Context Window Usage

Typical token usage per prompt:

| Component | Tokens | Example |
|-----------|--------|---------|
| System message | 2,000 | Type hints, docstrings, quality requirements |
| Prompt text | 1,000 | COMPLETE_SEQUENTIAL_PROMPTS.md section |
| Example code | 2,000 | ScanRun or similar reference model |
| Full conversation | 20,000+ | Growing as you work through week |

**Total per conversation:** 200K token window is very generous. You can easily build entire 25-model database in one conversation without context issues.

---

## 🚀 Recommended Workflow

### Option A: One Conversation Per Week

**Workflow:**
```
Week 3-4, Prompt 3.1: Create ScanRun → save to file
Week 3-4, Prompt 3.2: Create Subdomain (in same conv) → save
...
Week 3-4, Prompt 3.10: Create tests (in same conv) → save
All in ONE conversation thread
```

**Pros:**
- Claude remembers all models created
- Easy to maintain style consistency
- Less context passing needed

**Cons:**
- Conversation gets long
- Harder to export entire conversation

### Option B: One Conversation Per Prompt

**Workflow:**
```
New conversation for each prompt
Prompt 3.1: [System msg + PROMPT 3.1] → save
New conversation for Prompt 3.2 with [PROMPT 3.2 + ScanRun code] → save
...
```

**Pros:**
- Clean, focused conversations
- Easy to review single prompt

**Cons:**
- More context passing needed
- More setup (system message each time? Maybe not necessary)

**BETTER:** One per prompt but Claude maintains style consistency automatically through type hints and docstrings in COMPLETE_SEQUENTIAL_PROMPTS.md

---

## ✅ Final Context Checklist

For each new prompt:

- [ ] Read prompt completely from COMPLETE_SEQUENTIAL_PROMPTS.md
- [ ] Identify dependencies (what code does this need?)
- [ ] Find existing code for each dependency
- [ ] Copy exact prompt text
- [ ] Add context if dependencies exist
- [ ] Submit to Claude
- [ ] Get generated code
- [ ] Save to file
- [ ] Verify with quality gates
- [ ] Move to next prompt

---

**Last updated:** February 2026  
**Related:** [claude.md](claude.md), [restrictions.md](restrictions.md), [COMPLETE_SEQUENTIAL_PROMPTS.md](COMPLETE_SEQUENTIAL_PROMPTS.md)
