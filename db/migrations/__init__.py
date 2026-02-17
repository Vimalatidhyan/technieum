# db/migrations — root-level SQL-file migration scaffold.
# Use run_migrations(engine) from this package to apply NNN_*.sql files.
from db.migrations.runner import run_migrations  # noqa: F401

__all__ = ["run_migrations"]
