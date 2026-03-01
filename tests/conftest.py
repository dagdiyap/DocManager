import sys
import os
from pathlib import Path

# Add root directory to sys.path for absolute imports
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

# Set test environment variables
os.environ["SECRET_KEY"] = "test_secret_key_must_be_at_least_32_chars_long"
os.environ["CA_DATABASE_URL"] = "sqlite:///:memory:"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from ca_desktop.backend.src.main import app  # noqa: E402
from ca_desktop.backend.src import database, models  # noqa: E402

# Setup In-Memory DB with StaticPool for persistence across connections in tests
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create tables once for the test session."""
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Yield a database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Yield a TestClient with overridden database dependency."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[database.get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
