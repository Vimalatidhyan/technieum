# AI-Powered Vibe Coding System - ReconX Enterprise v2.0

## 🎯 Overview

This folder contains a **complete AI agent orchestration system** for building ReconX Enterprise using multiple AI tools simultaneously (VS Code Copilot, Claude Code, Cursor, etc.).

**Key Philosophy:** 
- ✅ Small, atomic tasks (each prompt handles ONE thing)
- ✅ Clear scope boundaries (agents know what NOT to do)
- ✅ Chainable prompts (one task leads to next)
- ✅ Quality gates (testing before proceeding)
- ❌ NO mega-prompts ("build entire project")

---

## 📁 Folder Structure

```
prompts-design/
├── README.md (you are here)
├── SYSTEM_PROMPTS.md            # Core instructions for all agents
├── AGENT_MANAGEMENT.md          # How to orchestrate multiple agents
├── IDE_STRATEGIES.md            # VS Code, Cursor, Claude strategies
├── QUALITY_GATES.md             # Testing & validation rules
├── 
├── week-1-2/
│   ├── CONTEXT.md               # Week context & goals
│   ├── PROMPTS.md               # All week's prompts
│   └── CHECKLIST.md             # Completion criteria
│
├── week-3-4/
├── week-5-6/
├── week-7-8/
├── week-9-10/
├── ... (all 16 weeks)
│
├── templates/
│   ├── ATOMIC_TASK_TEMPLATE.md # How to write atomic prompts
│   ├── API_ENDPOINT_TEMPLATE.md
│   ├── DB_MODEL_TEMPLATE.md
│   ├── MODULE_TEMPLATE.md
│   ├── TEST_TEMPLATE.md
│   └── INTEGRATION_TEMPLATE.md
│
├── utilities/
│   ├── PROMPT_DECOMPOSER.md    # Break big tasks into atomic ones
│   ├── VALIDATION_CHECKLIST.md # What to verify before moving on
│   ├── ERROR_RECOVERY.md       # When things go wrong
│   └── AGENT_COMMUNICATION.md  # How to talk to multiple agents
│
└── reference/
    ├── REPOSITORY_CONTEXT.md   # For pasting into agent context
    ├── API_REFERENCE.md        # Current API structure
    ├── DB_SCHEMA.md            # Database schema reference
    └── PROJECT_GLOSSARY.md     # Terms & abbreviations
```

---

## 🚀 Quick Start

### For Week 1 (Foundation)

1. **Read This First:**
   ```
   SYSTEM_PROMPTS.md         (5 min)
   AGENT_MANAGEMENT.md       (5 min)
   IDE_STRATEGIES.md         (5 min)
   ```

2. **Then Follow:**
   ```
   week-1-2/CONTEXT.md       (2 min)
   week-1-2/PROMPTS.md       (start coding)
   ```

3. **Use This Template:**
   ```
   Copy prompt from week-1-2/PROMPTS.md
   Paste into your AI tool (VS Code, Cursor, Claude)
   Wait for code generation
   Copy code to file
   Run tests (quality-gates)
   Move to next prompt
   ```

---

## 💡 Core Principles

### 1. Atomic Tasks (CRITICAL)
❌ DON'T: "Build the entire database layer"  
✅ DO: "Create ScanRun model with 5 fields and docstring"

Each prompt = **maximum 15 minutes of agent work**

### 2. Chainable Execution
```
Prompt 1 → Generated Code A
Prompt 2 → Generated Code B (uses A)
Prompt 3 → Tests for A+B
Prompt 4 → Integration of A+B+C
```

### 3. Quality Gates
Before moving to next prompt:
✅ Code runs without errors
✅ Tests pass
✅ Type hints correct
✅ Docstrings present

### 4. Multi-Agent Choreography
```
Agent 1 (VS Code):  Working on backend
Agent 2 (Cursor):   Working on tests simultaneously
Agent 3 (Claude):   Creating documentation
Agent 4 (ChatGPT):  Reviewing & QA

Result: Parallel development!
```

---

## 📋 How to Use Each Week

### Every Monday (Start of Week):

1. **Read the Context:**
   ```
   cat week-X/CONTEXT.md
   ```

2. **Understand the Goals:**
   - What are we building?
   - Why are we building it?
   - How does it fit into the larger project?

3. **Review the Prompts:**
   ```
   cat week-X/PROMPTS.md
   ```

4. **Start First Task:**
   ```
   Copy first prompt
   Paste into your AI tool
   Execute
   Verify with QUALITY_GATES.md
   Move to next prompt
   ```

5. **Check Off Completion:**
   ```
   cat week-X/CHECKLIST.md
   Mark items as done
   ```

### Every Evening:

- [ ] Run full test suite: `make test`
- [ ] Check git commits: `git log --oneline -5`
- [ ] Review coverage: `pytest --cov=backend`
- [ ] Update progress in week checklist

### Every Friday:

- [ ] Review week's progress
- [ ] All tests passing?
- [ ] 85%+ coverage?
- [ ] Ready for next week?
- [ ] If no: debug, don't move forward

---

## 🤖 Agent Types & Tools

### VS Code Copilot
**Best For:** Quick inline code completion, refactoring  
**Scope:** Single files, <100 lines  
**Trigger:** Start typing or `/` for commands

### Cursor IDE
**Best For:** Entire file generation, context-aware coding  
**Scope:** Single files, <500 lines  
**Trigger:** Cmd+K for chat

### Claude Code
**Best For:** Complex logic, multi-file reasoning  
**Scope:** Multiple files, architecture  
**Trigger:** Paste prompt + context

### ChatGPT (Web)
**Best For:** Documentation, explanations, QA  
**Scope:** Broad concepts, reviews  
**Trigger:** Paste task + requirements

### GitHub Copilot Chat (VS Code)
**Best For:** Testing, debugging, optimization  
**Scope:** Single feature, <50 lines  
**Trigger:** Cmd+Shift+I

---

## ⚡ Typical Workflow for One Task

**Example: Create Database Model**

```
1. PREPARATION (2 min)
   - Open week-X/PROMPTS.md
   - Find "Atomic Task: Create ScanRun Model"
   - Copy entire prompt (it has context!)

2. PASTE INTO AGENT (1 min)
   - Cursor IDE: Cmd+K, paste prompt
   - VS Code: Select file, /explain + paste
   - Claude: New conversation, paste prompt

3. GENERATION (2-5 min)
   - Agent generates code
   - Usually creates: model definition, docstrings, type hints

4. COPY CODE (1 min)
   - Copy generated code
   - Paste into backend/db/models.py (or specified file)

5. VERIFY (3 min)
   - Run: python -c "from backend.db.models import ScanRun; print(ScanRun)"
   - Check: No import errors
   - Check: All fields present

6. TEST (5 min)
   - Follow test prompt from week-X/PROMPTS.md
   - Run: pytest backend/tests/test_models.py::test_scanrun
   - Check: Test passes

7. COMMIT (1 min)
   - git add backend/db/models.py
   - git commit -m "feat: add ScanRun model with 5 fields"

8. MOVE ON (0 min)
   - Mark as ✅ in CHECKLIST
   - Start next prompt
```

**Total Time: 15 minutes per atomic task**

---

## 🎓 What Each File Does

### SYSTEM_PROMPTS.md
Core instructions that go into EVERY prompt's preamble.  
Think of it as the "constitution" for all agents.

```
Example format:
- Instruction 1: Code style (PEP 8, type hints)
- Instruction 2: Documentation (docstrings, comments)
- Instruction 3: Testing (what to test)
- Instruction 4: Scope (what NOT to do)
```

### AGENT_MANAGEMENT.md
How to coordinate multiple agents working simultaneously.

```
Includes:
- Agent roles (who does what)
- Communication protocol (how agents share context)
- Conflict resolution (if agents clash)
- Parallel execution strategy
```

### IDE_STRATEGIES.md
Specific techniques for each AI tool.

```
For each IDE:
- Keyboard shortcuts
- Context window best practices
- How to provide file context
- File size limits
- Best prompt structures
```

### week-X/CONTEXT.md
The "why" and "what" for that week.

```
Includes:
- Learning objectives
- Files you'll create
- Tests you'll write
- Dependencies with other weeks
- Success criteria
```

### week-X/PROMPTS.md
**The actual prompts you'll paste into agents.**

```
Each prompt:
1. Atomic task (clear, bounded)
2. Context lines <5 (background)
3. Requirements (what to generate)
4. Constraints (what NOT to do)
5. Example input/output
6. Success criteria
```

### Templates/
Pre-built structures for common tasks.

```
Use these as foundations:
- API_ENDPOINT_TEMPLATE.md → For creating endpoints
- DB_MODEL_TEMPLATE.md → For creating models
- TEST_TEMPLATE.md → For test files
(etc.)
```

---

## 🔄 Multi-Agent Workflow Example

### Scenario: Build ScanRun Database Model

**Timeline:**
```
Monday 9:00 AM  → Agent 1 (Cursor): Creates model
Monday 9:15 AM  → Agent 2 (VS Code): Simultaneously creates tests
Monday 9:30 AM  → Agent 3 (Claude): Documents in ARCHITECTURE.md
Monday 9:45 AM  → You: Review & verify all three
Monday 10:00 AM → All merged, ready for next task
```

**Commands for Each Agent:**

**Agent 1 (Cursor IDE):**
```
Cmd+K
Paste: week-3/PROMPTS.md → "Atomic Task: Create ScanRun Model"
Output: backend/db/models.py with ScanRun class
```

**Agent 2 (VS Code Copilot):**
```
New file: backend/tests/test_models_scanrun.py
/explain "Create comprehensive tests for ScanRun model"
Output: 20+ unit tests
```

**Agent 3 (Claude):**
```
New chat
Paste: SYSTEM_PROMPTS.md + week-3/CONTEXT.md
Request: "Add ScanRun model documentation to ARCHITECTURE.md"
Output: Documentation text ready to paste
```

**You:**
```
15:00 → Review all three outputs
15:15 → Copy code to actual files
15:30 → Run: make test (all pass?)
15:45 → git commit -m "feat: add ScanRun model with tests and docs"
16:00 → Done! Next task!
```

---

## 🎯 Week-by-Week Overview

### Week 1-2: Foundation
**Agents:** 2-3  
**Tasks:** 8-10  
**Time per task:** 10-15 min

### Week 3-4: Database
**Agents:** 3-4  
**Tasks:** 15-20  
**Time per task:** 12-15 min

### Week 5-6: Backend Orchestrator
**Agents:** 4  
**Tasks:** 10-15  
**Time per task:** 15-20 min

### Week 7-10: Intelligence Modules
**Agents:** 4-5  
**Tasks:** 30-40  
**Time per task:** 15-25 min

### Week 11-12: API Server
**Agents:** 4  
**Tasks:** 20-25  
**Time per task:** 15-20 min

### Week 13-14: Frontend UI
**Agents:** 3  
**Tasks:** 15-20  
**Time per task:** 20-25 min

### Week 15-16: Testing & Deployment
**Agents:** 3  
**Tasks:** 10-15  
**Time per task:** 15-20 min

---

## ⚠️ Common Mistakes to Avoid

### ❌ Mistake 1: Too-Large Prompts
```
WRONG: "Create the entire database layer"
RIGHT: "Create ScanRun model with these 5 fields"
```

### ❌ Mistake 2: Context Loss
```
WRONG: Copy prompt without context
RIGHT: Include SYSTEM_PROMPTS.md preamble + relevant context
```

### ❌ Mistake 3: No Quality Gates
```
WRONG: Accept generated code without testing
RIGHT: Run tests before moving to next task
```

### ❌ Mistake 4: Agent Collisions
```
WRONG: Two agents editing same file simultaneously
RIGHT: Each agent works on different files/tasks
```

### ❌ Mistake 5: Skipping Documentation
```
WRONG: Generate code-only, skip docs
RIGHT: Always generate code + tests + documentation
```

---

## ✅ Best Practices

### ✅ Practice 1: Atomic Scope
Each prompt: **ONE file, ONE feature, ~100-200 lines**

### ✅ Practice 2: Context Preamble
Every prompt starts with:
```
[SYSTEM_PROMPTS preamble]
[Week context]
[Specific task]
[Example]
[Success criteria]
```

### ✅ Practice 3: Verification Step
After generation:
```
1. Code has no syntax errors
2. Tests pass
3. Type hints correct
4. Docstrings present
5. Follows project style
```

### ✅ Practice 4: Commit Often
After EVERY atomic task:
```
git commit -m "feat: <one-liner>"
```

### ✅ Practice 5: Track Progress
After each week:
```
✅ mark as done in CHECKLIST.md
Record time taken
Note any issues
```

---

## 🚨 If Something Goes Wrong

**Problem:** Agent generates broken code

**Solution:**
1. Check: Did you include SYSTEM_PROMPTS.md preamble?
2. Ask agent: "Fix the following errors: [list]"
3. If still broken: Manually fix, then ask agent to explain
4. Learn: Update future prompts to prevent this

**Problem:** Agent skips requirements

**Solution:**
1. Create clearer prompt with examples
2. Use different agent (Cursor vs Claude often have different strengths)
3. Include explicit "MUST include" list

**Problem:** Two agents created conflicting code

**Solution:**
1. Stop, merge manually
2. Update AGENT_MANAGEMENT.md to prevent this
3. Assign tasks to different files

---

## 📊 Success Metrics

### Daily
- [ ] All tasks have atomic scope
- [ ] 100% of generated code tested
- [ ] 0 merge conflicts
- [ ] At least one commit per task

### Weekly
- [ ] All week's prompts used
- [ ] 85%+ test coverage
- [ ] All quality gates passed
- [ ] Ready for next week

### Per Agent
- [ ] Accuracy: 95%+ (code works)
- [ ] Consistency: Follows project style
- [ ] Efficiency: <15 min per task

---

## 🎓 How to Get Started

### Right Now (5 minutes):
1. Read this file (you're doing it!)
2. Read SYSTEM_PROMPTS.md
3. Read AGENT_MANAGEMENT.md

### Today (30 minutes):
1. Read IDE_STRATEGIES.md for your tools
2. Read week-1-2/CONTEXT.md
3. Review week-1-2/PROMPTS.md

### Tomorrow (execution):
1. Pick first prompt
2. Paste into your agent
3. Execute
4. Verify
5. Move to next

### This Week:
1. Complete all week-1-2 prompts
2. Run full test suite
3. Verify 85%+ coverage
4. Ready for week 3

---

## 📞 FAQ

**Q: Can I use all agents simultaneously?**  
A: YES! Assign each agent different tasks/files. They won't conflict if you manage scope well.

**Q: What if an agent can't follow my prompt?**  
A: Rephrase using simpler language. Or try a different agent (Claude often better for complex logic, Cursor for quick generation).

**Q: Do I need all advanced AI tools?**  
A: No! Start with free VS Code Copilot. Add others as needed: Cursor, Claude, ChatGPT.

**Q: How long does each task really take?**  
A: 10-20 min including: generation, verification, testing, committing.

**Q: Can I modify the prompts?**  
A: YES! Customize for your workflow. The structure is the recipe, you're the chef.

**Q: What if I get stuck?**  
A: Check ERROR_RECOVERY.md and QUALITY_GATES.md

---

## 🎬 Next Steps

1. **Read All Core Files** (30 min)
   ```
   cat SYSTEM_PROMPTS.md
   cat AGENT_MANAGEMENT.md
   cat IDE_STRATEGIES.md
   ```

2. **Read This Week** (10 min)
   ```
   cat week-1-2/CONTEXT.md
   cat week-1-2/PROMPTS.md
   ```

3. **Start Coding** (Execute prompts)
   ```
   Use PROMPT 1 from week-1-2/PROMPTS.md
   Choose your agent (Cursor/Claude/VS Code)
   Paste prompt
   Execute
   Verify with QUALITY_GATES.md
   Next prompt!
   ```

---

**You now have a complete AI-powered vibe coding system.**

**Start simple. Scale as you learn.**

**Execute atomically. Verify continuously.**

**Good luck! 🚀**
