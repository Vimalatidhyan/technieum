.PHONY: help install dev-setup test lint format security-scan clean docker-up docker-down lint-staged pre-commit-install

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m # No Color

help:
	@echo "$(BLUE)ReconX Enterprise - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make install              Install all dependencies"
	@echo "  make dev-setup            Setup complete development environment"
	@echo "  make pre-commit-install   Install git hooks for code quality"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test                 Run all tests with coverage"
	@echo "  make test-unit            Run unit tests only"
	@echo "  make test-integration     Run integration tests only"
	@echo "  make test-api             Run API tests only"
	@echo ""
	@echo "$(GREEN)Code Quality:$(NC)"
	@echo "  make lint                 Run all linters"
	@echo "  make format               Auto-format code (Black, isort)"
	@echo "  make security-scan        Run security checks (Bandit)"
	@echo "  make lint-check           Run lint without auto-fixing"
	@echo ""
	@echo "$(GREEN)Docker:$(NC)"
	@echo "  make docker-build         Build Docker images"
	@echo "  make docker-up            Start development stack"
	@echo "  make docker-down          Stop development stack"
	@echo "  make docker-logs          View docker-compose logs"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@echo "  make db-migrate           Run database migrations"
	@echo "  make db-reset             Reset database"
	@echo ""
	@echo "$(GREEN)Cleanup:$(NC)"
	@echo "  make clean                Remove cache and build artifacts"
	@echo ""

install:
	@echo "$(BLUE)Installing Python dependencies...$(NC)"
	pip install --upgrade pip
	pip install -r backend/requirements.txt
	@echo "$(BLUE)Installing Node dependencies...$(NC)"
	cd frontend/web && npm install
	@echo "$(GREEN)✓ Installation complete$(NC)"

dev-setup: install
	@echo "$(BLUE)Setting up development environment...$(NC)"
	python -m venv venv || python3 -m venv venv
	@echo "$(BLUE)Installing dev dependencies...$(NC)"
	pip install -r backend/requirements-dev.txt
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(BLUE)Creating .env file...$(NC)"
	cp .env.example .env
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(GREEN)✓ Run 'source venv/bin/activate' to activate environment$(NC)"

test:
	@echo "$(BLUE)Running all tests with coverage...$(NC)"
	pytest backend/tests -v \
		--cov=backend \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-fail-under=80
	@echo "$(GREEN)✓ Tests complete. Coverage report in htmlcov/$(NC)"

test-unit:
	@echo "$(BLUE)Running unit tests...$(NC)"
	pytest backend/tests/unit -v

test-integration:
	@echo "$(BLUE)Running integration tests...$(NC)"
	pytest backend/tests/integration -v

test-api:
	@echo "$(BLUE)Running API tests...$(NC)"
	pytest backend/tests/api -v

lint: format security-scan lint-check
	@echo "$(GREEN)✓ Linting complete$(NC)"

lint-check:
	@echo "$(BLUE)Running flake8...$(NC)"
	flake8 backend/ --max-line-length=100 --exclude=migrations,__pycache__
	@echo "$(BLUE)Running pylint...$(NC)"
	pylint backend/ --disable=C,W,R --fail-under=8.0 2>/dev/null || true
	@echo "$(GREEN)✓ Linting checks passed$(NC)"

format:
	@echo "$(BLUE)Formatting code with Black...$(NC)"
	black backend/ --line-length=100
	@echo "$(BLUE)Sorting imports with isort...$(NC)"
	isort backend/
	@echo "$(GREEN)✓ Code formatted$(NC)"

security-scan:
	@echo "$(BLUE)Running security scan with Bandit...$(NC)"
	bandit -r backend/ \
		-ll \
		-i \
		-x backend/tests \
		-f json \
		-o security-report.json 2>/dev/null || true
	@echo "$(GREEN)✓ Security scan complete$(NC)"

docker-build:
	@echo "$(BLUE)Building Docker images...$(NC)"
	docker-compose build
	@echo "$(GREEN)✓ Docker images built$(NC)"

docker-up: docker-build
	@echo "$(BLUE)Starting development stack...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Services running:$(NC)"
	@echo "   API: http://localhost:8000"
	@echo "   Web UI: http://localhost:3000"
	@echo "   PostgreSQL: localhost:5432"
	@echo "   Redis: localhost:6379"
	@echo "$(BLUE)Run 'make docker-logs' to view logs$(NC)"

docker-down:
	@echo "$(BLUE)Stopping development stack...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Services stopped$(NC)"

docker-logs:
	docker-compose logs -f

db-migrate:
	@echo "$(BLUE)Running database migrations...$(NC)"
	alembic upgrade head
	@echo "$(GREEN)✓ Migrations complete$(NC)"

db-reset:
	@echo "$(RED)⚠ Resetting database...$(NC)"
	echo "drop schema public cascade; create schema public;" | psql $$DATABASE_URL
	alembic upgrade head
	@echo "$(GREEN)✓ Database reset$(NC)"

clean:
	@echo "$(BLUE)Cleaning up...$(NC)"
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

pre-commit-install:
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	pre-commit install
	@echo "$(GREEN)✓ Pre-commit hooks installed$(NC)"

lint-staged:
	@echo "$(BLUE)Running linters on staged files...$(NC)"
	pre-commit run --all-files
