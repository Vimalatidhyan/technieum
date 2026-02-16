"""
Test configuration for backend API tests.

Patches database.SessionLocal to use test SQLite so the auth middleware
(which calls SessionLocal() directly) uses the same DB as test fixtures.
"""
import os

# Must be set BEFORE backend.db.database is imported
os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import backend.db.database as db_module

# Import models so they register on Base.metadata BEFORE create_all
import backend.db.models  # noqa: F401
from backend.db.base import Base

TEST_DB_URL = "sqlite:///./test_api.db"
_test_engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
_TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Patch module-level engine and SessionLocal so auth middleware uses test DB
db_module.engine = _test_engine
db_module.SessionLocal = _TestingSessionLocal

# Now create all tables (models are registered on Base.metadata)
Base.metadata.create_all(bind=_test_engine)
