"""SQLAlchemy declarative base and engine utilities.

Provides the Base class that all ORM models inherit from,
plus a factory for creating database engines.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


def get_engine(database_url: str, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine.

    Args:
        database_url: Database connection string
            (e.g. ``postgresql://user:pass@host/db``).
        echo: If True, log all SQL statements to stdout.

    Returns:
        Configured SQLAlchemy Engine instance.
    """
    return create_engine(database_url, echo=echo)


def get_session_factory(engine: Engine) -> sessionmaker:
    """Create a session factory bound to an engine.

    Args:
        engine: SQLAlchemy Engine to bind sessions to.

    Returns:
        Configured sessionmaker instance.
    """
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)
