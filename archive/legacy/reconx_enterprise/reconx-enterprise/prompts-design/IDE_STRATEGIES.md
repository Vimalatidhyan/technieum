# IDE-Specific Strategies
## How to Get the Best Results from Each AI Tool

---

## Overview

Different AI tools have different strengths. This guide shows how to use each one effectively.

```
VS Code Copilot    → Quick fixes, patterns, one-liners (FAST)
Cursor IDE         → Full file generation (BALANCED)
Claude Code        → Complex multi-file work (SMART)
ChatGPT            → Documentation, explanation (BROAD)
GitHub Copilot Chat → Testing, debugging (FOCUSED)
```

---

## 🔵 VS Code Copilot

### What It's Good At
- ✅ Completing patterns you start typing
- ✅ Suggesting next lines of code
- ✅ Quick one-liner fixes
- ✅ Filling in boilerplate
- ✅ Function completion

### What It's NOT Good At
- ❌ Creating entire new files
- ❌ Complex multi-step logic
- ❌ Understanding architectural decisions
- ❌ Explaining why (only what)

### Setup
1. Have VS Code open
2. Install "GitHub Copilot" extension (by GitHub)
3. Sign in with GitHub account
4. Start a `.py` file

### Best Techniques

#### Technique 1: Trigger Inline Suggestion
```python
# Type this:
def get_user_by_id(user_id: int) ->

# VS Code suggests:
def get_user_by_id(user_id: int) -> Dict[str, Any]:

# Press Tab to accept
```

#### Technique 2: Cmd+I for Inline Chat
```
1. Open file, place cursor where you want insertion
2. Press Cmd+I
3. Type: "Add docstring"
4. Select suggestion
5. Accept

Result: Docstring added in 10 seconds!
```

#### Technique 3: Multi-Line Completion
```python
def validate_email(email: str) -> bool:
    """Validate email format."""
    # Start typing next line:
    if not email or "@" not in email:  # Copilot completes this
        return False
    
    return True  # And this
```

#### Technique 4: Duplicate with Variations
```python
# First function exists:
def calculate_xss_risk(vulns: List[str]) -> int:
    return len(vulns) * 10

# Start typing similar function:
def calculate_sqli_risk(vulns: List[str]) ->
# Copilot suggests: len(vulns) * 15  (understands pattern!)

def calculate_rfi_risk(vulns: List[str]) ->
# Copilot suggests: len(vulns) * 12
```

### Command Reference
| Action | Command |
|--------|---------|
| Accept suggestion | Tab |
| Reject suggestion | Esc |
| See alternatives | Option+] |
| Open inline chat | Cmd+I |
| Close inline chat | Esc |

### Example: Building Test File

**Start:**
```python
import pytest
from backend.db.models import ScanRun

def test_scanrun
```

**Copilot autocompletes:**
```python
def test_scanrun_creation():
    scan = ScanRun(domain="example.com")
    assert scan.domain == "example.com"
```

**Copilot sees pattern:**
```python
def test_scanrun_status():
    scan = ScanRun(status="pending")
    assert scan.status == "pending"
```

*Speed: 5 minutes for 15 test functions*

### Tips
1. **Use comments as hints**
   ```python
   # Function to calculate risk score
   def calculate_risk(
   # ↑ Copilot uses comment to suggest smarter completions
   ```

2. **Show pattern first**
   ```python
   # Bad: Ask Copilot to create from nothing
   def 
   
   # Good: Create one function, let Copilot repeat pattern
   def parse_xss(data):
       return extract_value(data)
   
   def parse_sqli(data):
       # Copilot knows you want similar signature
   ```

3. **Use structure as guide**
   ```python
   class Result:
       def __init__(self, success: bool):
       # Copilot suggests: self.success = success
   ```

---

## 🟢 Cursor IDE

### What It's Good At
- ✅ Generating complete `.py` files (100-500 lines)
- ✅ Understanding context from multiple files
- ✅ Creating well-structured code
- ✅ Following project conventions
- ✅ Fastest for "generate full feature"

### What It's NOT Good At
- ❌ One-line fixes (overkill)
- ❌ Complex reasoning (no multi-turn)
- ❌ Learning from feedback (each chat starts fresh)

### Setup
1. Download Cursor IDE (https://www.cursor.sh/)
2. Open your `reconx-enterprise` project
3. Use Cmd+K to open chat
4. Make sure `.cursorrules` file exists (for context)

### Best Techniques

#### Technique 1: Cmd+K Generate from Scratch
```
1. Create new file: backend/db/models.py
2. Press Cmd+K
3. Paste this:

[SYSTEM_PROMPTS.md preamble]
[Week 3 context]

TASK: Create ScanRun model with these exact fields:
- id (primary key)
- domain (varchar 255, unique)
- status (varchar 50, default pending)
- scan_type (varchar 50)
- created_at (datetime)

4. Press Enter
5. Cursor generates full file
```

**Result:** 50-line file created instantly ✅

#### Technique 2: Cmd+K with File Reference
```
1. Open existing file as reference
2. Create new file
3. Cmd+K + paste prompt that references the existing file:

"Create API endpoints for the ScanRun model
(reference: src/db/models.py has ScanRun definition)
Follow the same patterns as existing endpoints"

4. Cursor uses both files for context!
```

#### Technique 3: Cmd+K for Refactoring
```
1. Open file with messy code
2. Select code block
3. Cmd+K:

"Refactor the selected code to:
- Add type hints
- Add docstrings
- Follow PEP 8"

4. Cursor refactors in place
```

#### Technique 4: Multiple Files in One Chat
```
1. Open main file you're working on
2. Hold Cmd and click additional files to add context
3. Cmd+K with prompt:

"Using the structure in models.py and following patterns in routes.py,
create a new route handler for domain scanning"

4. Cursor has access to both files!
```

### Command Reference
| Action | Command |
|--------|---------|
| Open chat | Cmd+K |
| Inline edit | Cmd+Shift+K |
| Generate | Enter |
| Cancel | Esc |
| Accept | Click "Accept" button |
| Edit generation | Type feedback on right side |
| Clear chat | Cmd+L |

### Example: Generate Complete Module

**Prompt:**
```
[SYSTEM_PROMPTS preamble]

Project structure:
- backend/db/models.py [exists, has ScanRun]
- backend/api/routes/ [existing routes as reference]

TASK: Create complete API endpoint file
File: backend/api/routes/scans.py
Requirements:
- Have POST /scans endpoint to create scan
- Have GET /scans/{scan_id} to retrieve scan
- Use ScanRun model from db.models
- Include Pydantic schemas
- Full docstrings
- Type hints everywhere
- Follow existing route patterns

Example request:
{
  "domain": "example.com",
  "scan_type": "full"
}
```

**Result:** 150-line API file with all endpoints ✅

### Time Estimate
- Simple file (models): 3-5 min
- Complex file (routes with logic): 8-12 min
- With fixes/refinement: 12-15 min

### Tips
1. **Provide existing code as reference**
   ```
   Include: "Follow the patterns in [existing_file]"
   Cursor uses it to match style
   ```

2. **Use file context**
   - Keep models.py open while generating tests
   - Keep routes.py open while generating new endpoints
   - Cursor can see all open files!

3. **Iterate with feedback**
   ```
   Initial: "Create the module"
   Feedback: "Added type hints, but missing docstrings"
   Cursor refines based on feedback
   ```

4. **Ask for multiple things**
   ```
   "Create:
   1. The model definition
   2. Database migration
   3. Test file
   
   All in one chat!"
   ```

---

## 🟣 Claude Code

### What It's Good At
- ✅ Complex reasoning across files
- ✅ Understanding architecture
- ✅ Multi-step solutions
- ✅ Debugging complex issues
- ✅ Testing strategy

### What It's NOT Good At
- ❌ Quick one-liners (overkill)
- ❌ Real-time editing (copy/paste workflow)

### Setup
1. Go to https://claude.ai
2. If using Claude Code extension in VS Code:
   - Install "Claude" by Anthropic
   - Enable code editing
3. Have your project files ready to paste

### Best Techniques

#### Technique 1: Full Context Paste
```
Include:
1. SYSTEM_PROMPTS.md (copy-paste top section)
2. Week context (from prompts-design/week-X/)
3. Existing code examples (from project)
4. Specific task

Claude uses ALL context to reason better
```

#### Technique 2: Ask for Multi-File Solutions
```
"I need to build a risk scoring feature.

Currently have:
- backend/db/models.py [paste model definition]
- backend/tests/test_models.py [paste existing test]

Need:
1. Create backend/intelligence/risk_scorer.py with:
   - Function: calculate_score(vulnerabilities)
   - Tests showing how it works
   - Integration example

2. Update backend/api/routes/scans.py to:
   - Add scoring endpoint
   - Include in response

Show me the changes needed in both files"
```

**Claude provides:**
- Complete risk_scorer.py
- Updated routes code
- Test examples
- Integration instructions

#### Technique 3: Design Discussion Before Coding
```
"Before I write code, I want to design our data model for:
- Scanner results storage
- Vulnerability classification
- Risk scoring

Current constraints:
- [list constraints]

What's the best approach?
- What tables do we need?
- What relationships?
- Any trade-offs?"

Then: "Perfect, now generate the SQLAlchemy models"
```

#### Technique 4: Debugging with Context
```
"This code is failing with error: [error message]

Context:
[database model code]
[API endpoint code]
[test that's failing]

The test: [test code]
Expected: [what should happen]
Actual: [what's happening]

What's wrong?"

Claude: [Full analysis + fixed code]
```

### Command Reference
| Action | Command |
|--------|---------|
| New chat | Cmd+Shift+A or click "+" |
| Edit message | Click pencil on your message |
| Copy code block | Click copy button on code |
| Use in VS Code | Install Claude extension + click "Edit in VS Code" |

### Example: Comprehensive Feature Design

**First Message:**
```
CONTEXT:
[Paste SYSTEM_PROMPTS.md]
[Paste week-5 context about orchestrator]

PROJECT:
We're building ReconX Enterprise - vulnerability scanning platform.
Goal: Create module to orchestrate scanning across multiple tools (Nmap, Burp, etc.)

Currently have:
- Database models for scans
- Basic API endpoints
- No orchestration layer

QUESTION: How should I architect the orchestrator?
- Should it be in separate module?
- How to handle async/parallel scans?
- State management approach?
```

**Claude Response:**
- Detailed architecture recommendations
- Pros/cons of different approaches
- Code structure examples
- Data flow diagrams (ASCII)

**Second Message:**
```
Perfect! Now please generate:

1. backend/orchestrator/base.py
   - AbstractOrchestrator class
   - Defines interface for scanners

2. backend/orchestrator/nmap_orchestrator.py
   - Concrete implementation for Nmap
   - Integration with our database

3. backend/orchestrator/__init__.py
   - Export the classes

Include:
- Type hints
- Docstrings
- Error handling
- Async/await patterns
```

**Claude Response:**
- All three files complete
- Integration ready
- Follows conventions

### Time Estimate
- Design discussion: 10-20 min
- Code generation: 5-10 min
- Refinement: 5-10 min
- Total: 20-40 min per complex feature

### Tips
1. **Start with Why, then What**
   ```
   Bad: "Generate this code"
   Good: "Here's the problem... What approach do you recommend?"
           "Perfect! Now generate the code..."
   ```

2. **Paste complete existing code**
   ```
   Don't: "I have models" [snippets]
   Do: [Full models.py file pasted]
   Better context = Better code
   ```

3. **Ask for test strategy first**
   ```
   "Given this requirement, what should I test?
    What are edge cases?"
   
   Then: "Now generate test file with those tests"
   ```

4. **Use for code review**
   ```
   "I generated this code. Does it:
   - Follow our conventions?
   - Have sufficient test coverage?
   - Handle errors well?
   
   [paste code]"
   ```

---

## 🟠 ChatGPT (Web)

### What It's Good At
- ✅ Explanations (why something doesn't work)
- ✅ Documentation writing
- ✅ Quick answers to questions
- ✅ Code review feedback
- ✅ Creating examples

### What It's NOT Good At
- ❌ Complex code generation (less reliable than Claude)
- ❌ Production-critical features
- ❌ Multi-file coordination

### Setup
1. Go to https://chat.openai.com
2. Start new chat
3. Paste code/questions

### Best Techniques

#### Technique 1: Quick Explanations
```
Problem: Got error - "UnboundLocalError: local variable referenced before assignment"

Code:
[paste code]

Q: What's wrong?

A: [ChatGPT explains error, shows fix, provides corrected code]
```

#### Technique 2: Documentation Generation
```
Code:
[paste module]

Please write:
1. README explaining how to use this module
2. Docstrings for each function
3. Example usage code

Format as markdown so I can paste into docs/
```

#### Technique 3: Code Review Checklist
```
I need to review this code for production deployment.

Code:
[paste]

Check for:
- Security issues
- Performance problems
- Missing error handling
- Test coverage
- Style consistency
- Type hints

Provide: [List of issues with fix suggestions]
```

#### Technique 4: Architecture Questions
```
I'm designing the intelligence module for scanning.

Current state:
[describe]

Questions:
1. Should risk scoring be synchronous or async?
2. How to handle dependencies between checks?
3. What's the best way to store partial results?

Requirements:
- [list constraints]
```

### Example: Generate Architecture Doc

```
I need comprehensive documentation for our API.

Current state:
- 15 endpoints across 3 route files
- Endpoints handle CRUD for Scans, Domains, Results
- Uses FastAPI
- All endpoints have docstrings

Please write "docs/API_ARCHITECTURE.md" that includes:
1. Overview of API design
2. Authentication approach (we'll add this week)
3. Each resource with endpoints
4. Example requests/responses
5. Error handling
6. Rate limiting strategy

Use markdown format, ~2000 words
```

**Result:** Complete API documentation ready to paste

### Command Reference
| Action |  Command |
|--------|----------|
| New chat | Click "+" bottom left |
| Copy response | Hover and click copy icon |
| Edit prompt | Click pencil on your message |
| Share chat | Click "..." menu |

### Time Estimate
- Explanations: 2-5 min
- Documentation: 10-20 min
- Code review: 10-15 min
- Q&A: 5-10 min

### Tips
1. **Be specific**
   ```
   Bad: "Check this code"
   Good: "Check this code for SQL injection vulnerabilities"
   ```

2. **Provide context**
   ```
   Bad: [just paste code]
   Good: "This is a FastAPI endpoint that accesses PostgreSQL..."
         [paste code]
   ```

3. **Ask for specific format**
   ```
   "Write this as markdown"
   "Create a table with two columns"
   "Use examples"
   ```

---

## 🔴 GitHub Copilot Chat (VS Code)

### What It's Good At
- ✅ Fixing errors in open file
- ✅ Writing tests for visible code
- ✅ Quick explanation of code
- ✅ Optimization suggestions

### What It's NOT Good At
- ❌ Creating new files (use Cursor instead)
- ❌ Complex multi-file work (use Claude instead)

### Setup
1. VS Code with GitHub Copilot extension
2. Cmd+Shift+I opens chat panel
3. Works on currently open file

### Best Techniques

#### Technique 1: Test Generation
```
1. Open function in VS Code
2. Cmd+Shift+I
3. Ask: "Generate comprehensive tests for this function"

Copilot:
- Creates test_functions.py
- Covers multiple cases
- Copy to your test file
```

#### Technique 2: Fix Error
```
1. See red error line
2. Cmd+Shift+I (or icon suggestion)
3. Describe: "Fix this error, explain why"

Copilot:
- Shows fix with explanation
- Click "Apply" to accept
```

#### Technique 3: Explain Code
```
1. Select code block
2. Cmd+Shift+I
3. Ask: "Explain what this code does"

Returns: Plain English explanation
```

---

## 🎯 Tool Selection Cheat Sheet

**Choose by task:**

| Task | Tool | Time | Quality |
|------|------|------|---------|
| One-liner fix | VS Code | 30s | High |
| Function completion | VS Code | 2 min | High |
| Full file generation | Cursor | 5-10 min | High |
| Complex multi-file | Claude | 15-30 min | Highest |
| Documentation | ChatGPT | 10-20 min | High |
| Test generation | Cursor or Chat | 5-10 min | High |
| Code explanation | ChatGPT or Chat | 2-5 min | High |
| Architecture | Claude | 20-40 min | Highest |
| Debug issue | Claude | 10-20 min | High |
| Review code | ChatGPT | 10-15 min | High |

---

## 🔄 Multi-Tool Workflow Example

**Scenario: Build Risk Scoring Feature**

```
Monday 9:00 AM
│
├─ Claude: Design architecture
│  Input: "How should risk scoring work?"
│  Output: Architecture recommendations
│
├─ Cursor: Generate risk_scorer.py
│  Input: [prompt with Claude's design]
│  Output: Complete module
│
├─ VS Code Copilot: Add to existing API
│  Input: Start typing, Copilot completes
│  Output: Integration code
│
├─ Cursor: Generate test file
│  Input: Cmd+K with risk_scorer.py reference
│  Output: Comprehensive tests
│
├─ ChatGPT: Document feature
│  Input: [All code files]
│  Output: Documentation
│
└─ You: Review & commit
   Result: Feature complete!
   Time: 2 hours (parallel work)
```

---

## ✅ Quality Checklist (For ANY Tool)

After getting code from ANY agent:

- [ ] Run: `python -c "import module_name"` (no errors)
- [ ] Run: `make lint` (formatting OK)
- [ ] Run: `make test` (tests pass)
- [ ] Coverage: Check specific file
- [ ] Review: Read the code (makes sense?)
- [ ] Git: Commit once verified

---

## 📞 Troubleshooting

### Problem: Tool generates wrong code

**Solution by tool:**
- VS Code: Accept what comes after, not perfect
- Cursor: Rephrase prompt, try again
- Claude: Ask "Why did you do X? Can you change to Y?"
- ChatGPT: Clearer examples of what you want

### Problem: Tool doesn't understand requirements

**Solution:**
```
1. Include more context
2. Show example of expected output
3. Be more specific/fewer words
4. Try different tool (different strengths)
```

### Problem: Tool is too slow

**Solution:**
- Use VS Code for quick completion
- Use Cursor for faster generation than you typing
- Use ChatGPT only for non-code tasks

### Problem: Different tools gave conflicting code

**Solution:**
```
1. Manual merge (keep best parts)
2. Ask Claude to review both and recommend
3. Document which tool for which task types
4. Standardize approach
```

---

## 🎓 Summary

- **VS Code Copilot:** Day-to-day workhorse, patterns, quick fixes (5 min/task)
- **Cursor:** Full file generation, balanced speed/quality (10 min/file)
- **Claude:** Complex design, multi-file, reasoning (20 min/feature)
- **ChatGPT:** Documentation, Q&A, reviews (15 min/output)
- **GitHub Copilot Chat:** Testing, debugging, explaining (5 min/task)

**Best practice:** Use the right tool for the job, combine for speed and quality.

**You now have a dream team of AI assistants!** 🚀
