"""Database connection and session management for License Server."""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import get_settings

# Base class for models
Base = declarative_base()

# Database engine (will be initialized in create_engine_from_settings)
engine = None
SessionLocal = None


def create_engine_from_settings() -> None:
    """Create database engine from settings."""
    global engine, SessionLocal

    settings = get_settings()

    database_url = settings.database_url_str

    # SQLite-specific arguments
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        engine = create_engine(
            database_url,
            connect_args=connect_args,
            echo=settings.debug,
        )
    else:
        # PostgreSQL/Production settings
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.debug,
        )

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session (FastAPI dependency).

    Yields:
        Database session
    """
    if SessionLocal is None:
        create_engine_from_settings()

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database (create tables)."""
    if engine is None:
        create_engine_from_settings()

    # Import models to register them
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
