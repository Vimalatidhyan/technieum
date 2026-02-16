"""Database migration framework.

Implements Alembic-compatible migration semantics without the Alembic dependency.
Migrations are sequential, version-tracked, and reversible.

Usage:
    from app.db.migrations import run_migrations
    run_migrations(engine)   # upgrade to latest
"""
from app.db.migrations.runner import run_migrations, get_current_version  # noqa: F401
