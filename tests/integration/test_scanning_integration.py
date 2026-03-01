import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil
from unittest.mock import patch

from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import database, models, dependencies

# Setup local test data
TEST_DOCS_ROOT = Path("/tmp/docmanager_test/documents")
TEST_SHARED_ROOT = Path("/tmp/docmanager_test/shared")


@pytest.fixture(scope="module")
def client():
    if TEST_DOCS_ROOT.exists():
        shutil.rmtree(TEST_DOCS_ROOT)
    TEST_DOCS_ROOT.mkdir(parents=True)

    # Create a test client folder
    client_phone = "9876543210"
    year_dir = TEST_DOCS_ROOT / client_phone / "2024"
    year_dir.mkdir(parents=True)

    # Create dummy PDF
    dummy_pdf = year_dir / "ITR.pdf"
    dummy_pdf.write_bytes(b"%PDF-1.4 mock content")

    # Setup In-Memory DB with StaticPool
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    models.Base.metadata.create_all(bind=engine)

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[database.get_db] = override_get_db

    # Create Test Client in DB
    db = TestingSessionLocal()
    test_client = models.Client(
        phone_number=client_phone,
        name="Test User",
        email="test@example.com",
        password_hash="fakehash",
        is_active=True,
    )
    db.add(test_client)
    db.commit()
    db.close()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = {}
    if TEST_DOCS_ROOT.exists():
        shutil.rmtree(TEST_DOCS_ROOT)


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CA Desktop Backend Online" in response.json()["status"]


def test_document_scanning(client):
    # Trigger scan
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.documents_root = TEST_DOCS_ROOT

        # Mock authentication
        app.dependency_overrides[dependencies.get_current_ca] = lambda: models.User(
            id=1, username="test_ca"
        )

        response = client.get("/api/v1/documents/scan")
        assert response.status_code == 202

    del app.dependency_overrides[dependencies.get_current_ca]
