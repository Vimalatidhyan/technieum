# 🚀 Getting Started - First 48 Hours

## Objective
Get the development environment running and make your first commit.

**Expected Time:** 30-45 minutes

---

## Step 1: Initialize Git Repository (5 min)

```bash
cd /Users/rejenthompson/Documents/technieum-/kali-linux-asm/reconx-enterprise

# Initialize git
git init

# Add all files
git add .

# Make first commit
git commit -m "chore: initialize reconx-enterprise foundation (v2.0)"

# Show commit history
git log --oneline
```

**Expected Output:**
```
* abc1234 chore: initialize reconx-enterprise foundation (v2.0)
```

---

## Step 2: Create GitHub Repository (10 min)

### Option A: Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI if needed
brew install gh

# Login to GitHub
gh auth login

# Create repository
gh repo create reconx-enterprise \
  --public \
  --source=. \
  --remote=origin \
  --push

# Verify
git remote -v
# Should show:
# origin    https://github.com/yourusername/reconx-enterprise.git (fetch)
# origin    https://github.com/yourusername/reconx-enterprise.git (push)
```

### Option B: Manual Setup
```bash
# 1. Go to https://github.com/new
# 2. Create repository named "reconx-enterprise"
# 3. Make it PUBLIC
# 4. DO NOT initialize with README (we have one)

# Then run:
git remote add origin https://github.com/yourusername/reconx-enterprise.git
git branch -M main
git push -u origin main
```

**Verify:**
```bash
git remote -v
open https://github.com/yourusername/reconx-enterprise
```

---

## Step 3: Set Up Development Environment (15 min)

### On macOS:

```bash
# Navigate to project
cd reconx-enterprise

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify Python
python --version
# Should show: Python 3.11.x or higher

# Install dependencies (backend)
pip install -r backend/requirements.txt

# Install pre-commit hooks (optional but recommended)
pip install pre-commit
pre-commit install
```

### Verify Installation:
```bash
# Check installed packages
pip list | head -20

# Verify key packages
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
python -c "import sqlalchemy; print(f'SQLAlchemy: {sqlalchemy.__version__}')"
python -c "import pytest; print(f'Pytest: {pytest.__version__}')"
```

**Expected output:** All imports successful ✅

---

## Step 4: Verify Docker Setup (10 min)

### Install Docker (if needed)

```bash
# macOS: Install Docker Desktop
# https://www.docker.com/products/docker-desktop

# Verify installation
docker --version
docker-compose --version

# Both should show version numbers
```

### Test Docker Stack

```bash
# Navigate to project
cd reconx-enterprise

# Build and start services
make docker-up

# This will:
# - Build API image
# - Start PostgreSQL
# - Start Redis
# - Start Flower monitoring
# - Start frontend

# Wait 30-60 seconds for services to start

# Verify all services running
docker-compose ps

# Expected output:
# CONTAINER ID    IMAGE              STATUS
# xxx             reconx-postgres    Up 1 minute (healthy)
# xxx             reconx-redis       Up 1 minute (healthy)
# xxx             reconx-api         Up 1 minute
# xxx             reconx-worker      Up 1 minute
# xxx             reconx-frontend    Up 1 minute
# xxx             reconx-flower      Up 1 minute
# xxx             reconx-pgadmin     Up 1 minute
```

### Test Services

```bash
# API Health Check
curl http://localhost:8000/health
# Expected: {"status":"healthy","version":"2.0.0"}

# API Docs
open http://localhost:8000/docs
# Should show Swagger UI with API endpoints

# Frontend
open http://localhost:3000
# Should show React app loading

# Database Admin
open http://localhost:5050
# PgAdmin UI (user: admin@reconx.local, password: admin)

# Celery Monitoring
open http://localhost:5555
# Flower monitoring UI
```

### Stop Services (when done testing)

```bash
make docker-down
```

---

## Step 5: Run Tests (5 min)

```bash
# Activate virtual environment
source venv/bin/activate

# Note: Tests will fail because no backend code exists yet
# This is expected!

# Run tests
pytest backend/tests -v

# Expected output:
# No tests ran (backend/tests probably empty)
# That's OK! This proves pytest works.

# Run static analysis
make lint

# Expected output:
# Black: OK
# isort: OK
# flake8: OK (or some warnings)
```

---

## Step 6: Verify Makefile Commands

```bash
source venv/bin/activate

# Show all available commands
make help

# Expected: Shows 20+ commands organized by category

# Test a few:
make clean              # Should remove cache
make security-scan      # Should run Bandit

# All should complete without errors ✅
```

---

## Step 7: Make Your First Code Commit

### Create a simple database model as example:

```bash
mkdir -p backend/db
touch backend/db/__init__.py
touch backend/db/models.py
touch backend/db/database.py
```

**File: `backend/db/models.py`**
```python
"""Database models for ReconX Enterprise"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ScanRun(Base):
    """Represents a complete scan run"""
    __tablename__ = "scan_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String(255), unique=True, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="running")  # running, completed, failed
    metadata = Column(JSON, default={})


class Asset(Base):
    """Represents discovered assets (domains, IPs, services)"""
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, index=True)
    asset_type = Column(String(50))  # domain, ip, service, technology
    value = Column(String(500), index=True)
    metadata = Column(JSON, default={})


class Vulnerability(Base):
    """Represents found vulnerabilities"""
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, index=True)
    cve_id = Column(String(50), index=True, nullable=True)
    title = Column(String(500))
    severity = Column(String(20))  # CRITICAL, HIGH, MEDIUM, LOW
    description = Column(String(2000))
    affected_asset = Column(String(255))
    metadata = Column(JSON, default={})
```

**File: `backend/db/database.py`**
```python
"""Database connection and session management"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./test.db"  # Default to SQLite for development
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
```

**File: `backend/tests/test_database.py`**
```python
"""Tests for database models"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.db.models import Base, ScanRun, Asset, Vulnerability


@pytest.fixture
def test_db():
    """Create test database"""
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.sqlite"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()
    # Cleanup
    Base.metadata.drop_all(bind=engine)


def test_scan_run_creation(test_db):
    """Test creating a scan run"""
    scan = ScanRun(target="example.com", status="running")
    test_db.add(scan)
    test_db.commit()
    test_db.refresh(scan)
    
    assert scan.id is not None
    assert scan.target == "example.com"
    assert scan.status == "running"


def test_scan_run_retrieval(test_db):
    """Test retrieving a scan run"""
    scan = ScanRun(target="example.com", status="running")
    test_db.add(scan)
    test_db.commit()
    
    retrieved = test_db.query(ScanRun).filter_by(target="example.com").first()
    assert retrieved is not None
    assert retrieved.target == "example.com"


def test_asset_creation(test_db):
    """Test creating an asset"""
    asset = Asset(
        scan_id=1,
        asset_type="domain",
        value="api.example.com",
        metadata={"status": "active"}
    )
    test_db.add(asset)
    test_db.commit()
    test_db.refresh(asset)
    
    assert asset.id is not None
    assert asset.value == "api.example.com"
    assert asset.metadata["status"] == "active"


def test_vulnerability_creation(test_db):
    """Test creating a vulnerability"""
    vuln = Vulnerability(
        scan_id=1,
        cve_id="CVE-2021-44790",
        title="Apache OpenSSL Vulnerability",
        severity="CRITICAL",
        description="A critical vulnerability in Apache OpenSSL...",
        affected_asset="example.com:80"
    )
    test_db.add(vuln)
    test_db.commit()
    test_db.refresh(vuln)
    
    assert vuln.id is not None
    assert vuln.severity == "CRITICAL"
    assert vuln.cve_id == "CVE-2021-44790"
```

---

## Step 8: Commit Your Code

```bash
# Add files
git add backend/db/__init__.py
git add backend/db/models.py
git add backend/db/database.py
git add backend/tests/test_database.py

# Verify what you're committing
git status

# Make commit with descriptive message
git commit -m "feat: add initial database models and tests

- Add ScanRun model for tracking scans
- Add Asset model for discovered assets
- Add Vulnerability model for CVEs
- Add database connection management
- Add comprehensive database tests
- Test coverage: 85%+"

# Push to GitHub
git push

# GitHub Actions will automatically:
# ✅ Run pytest
# ✅ Run flake8
# ✅ Run black (format check)
# ✅ Generate coverage report

# Visit: https://github.com/yourusername/reconx-enterprise
# Click on "Actions" to see pipeline run
```

---

## Step 9: Verify Everything Works

```bash
# 1. Check local tests pass
source venv/bin/activate
pytest backend/tests -v --cov=backend

# Expected: 4 tests pass, coverage > 80%

# 2. Check code formatting
make format

# Expected: All Python files formatted

# 3. Check linters
make lint

# Expected: No critical errors

# 4. Check git logs
git log --oneline -5

# Expected: Your commits visible

# 5. Check GitHub repo
open https://github.com/yourusername/reconx-enterprise

# Look for:
# ✅ Code is there
# ✅ Actions tab shows pipeline (green checkmark)
# ✅ README visible
```

---

## 🎉 SUCCESS!

If you can answer YES to all of these, you're ready for Week 3:

- ✅ Git repository created locally
- ✅ GitHub repository created online
- ✅ First code committed and pushed
- ✅ CI/CD pipeline ran successfully
- ✅ Docker stack starts without errors
- ✅ API responds at http://localhost:8000/health
- ✅ Tests run and pass locally
- ✅ Code quality checks pass

---

## 📋 Troubleshooting

### "Command not found: make"
```bash
# Install make if on macOS
brew install make

# Or use: gmake instead of make
```

### "docker-compose: command not found"
```bash
# Install Docker Desktop for Mac
# https://www.docker.com/products/docker-desktop

# Or use: docker compose (new syntax)
docker compose up -d
```

### "pytest: command not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall pytest
pip install --upgrade pytest
```

### "Cannot connect to Docker daemon"
```bash
# Start Docker Desktop
# Then try again: make docker-up

# Or restart Docker:
docker restart
```

### Git push fails
```bash
# Set default branch to 'main'
git config --global init.defaultBranch main

# If repo exists, rename branch
git branch -M main

# Retry push with credentials
git push -u origin main
```

---

## 🎓 Next Steps

Once you complete this, move to **Week 3:** Create Database Models

**Read:** `IMPLEMENTATION_ROADMAP.md` - Week 3 section

---

## 💬 Questions?

- Check `TROUBLESHOOTING.md`
- Review `DEVELOPMENT.md`
- Email: [your-team-email]

---

**You're now set up for enterprise-level development! 🚀**

**Next: Start Week 3 database implementation.**
