import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from ca_desktop.backend.src.database import Base, get_db
from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import models
from ca_desktop.backend.src.dependencies import get_current_user_data

# Setup in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


Base.metadata.create_all(bind=engine)
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    yield db
    db.rollback()
    db.close()


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user_data] = lambda: {
        "user_id": 1,
        "user_type": "ca",
        "phone_number": None,
    }
    yield TestClient(app)
    app.dependency_overrides.pop(get_current_user_data, None)


@pytest.fixture
def tmp_upload_root(tmp_path):
    with patch("ca_desktop.backend.src.routers.ca_profile.get_settings") as mock_settings:
        mock_settings.return_value.documents_root = str(tmp_path / "docs")
        yield tmp_path


def seed_ca_user(db):
    db.query(models.CAMediaItem).delete()
    db.query(models.Service).delete()
    db.query(models.CAProfile).delete()
    db.query(models.User).delete()
    db.commit()
    ca = models.User(
        id=1, username="admin", email="admin@test.com", password_hash="hash"
    )
    db.add(ca)
    db.commit()
    return ca


def test_get_update_profile(client, db_session):
    seed_ca_user(db_session)

    # 1. Get empty profile (auto-create)
    response = client.get("/api/v1/ca/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["firm_name"] is None

    # 2. Update profile
    payload = {
        "firm_name": "Test Firm",
        "professional_bio": "Bio",
        "email": "firm@test.com",
    }
    response = client.patch("/api/v1/ca/profile", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["firm_name"] == "Test Firm"
    assert data["email"] == "firm@test.com"


def test_media_upload(client, db_session, tmp_upload_root):
    seed_ca_user(db_session)

    file_content = b"fake image"
    files = {"file": ("logo.jpg", file_content, "image/jpeg")}
    data = {"item_type": "carousel", "title": "Office", "order_index": 0}

    response = client.post("/api/v1/ca/media", files=files, data=data)
    print(f"Response: {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert data is not None, f"Response JSON is None. Text: {response.text}"
    assert data["item_type"] == "carousel"
    assert "logo.jpg" in data["file_path"]

    # Verify file saved
    # Path: tmp_path / "uploads" / "1" / "carousel" / "logo.jpg"
    saved_path = tmp_upload_root / "uploads" / "1" / "carousel" / "logo.jpg"

    print(f"Checking path: {saved_path}")
    if not saved_path.exists():
        print(f"Path does not exist. Listing tmp_upload_root ({tmp_upload_root}):")
        import os

        for root, dirs, files in os.walk(tmp_upload_root):
            print(f"{root}:")
            for d in dirs:
                print(f"  d: {d}")
            for f in files:
                print(f"  f: {f}")

    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content


def test_media_upload_invalid_type(client, db_session):
    seed_ca_user(db_session)

    file_content = b"exe content"
    files = {"file": ("malware.exe", file_content, "application/octet-stream")}
    data = {"item_type": "carousel"}

    response = client.post("/api/v1/ca/media", files=files, data=data)
    assert response.status_code == 400
    assert "extension" in response.json()["detail"]


def test_service_crud(client, db_session):
    seed_ca_user(db_session)

    # Create
    response = client.post(
        "/api/v1/ca/services",
        params={"name": "Audit", "description": "Statutory Audit"},
    )
    assert response.status_code == 200
    svc_id = response.json()["id"]

    # List
    response = client.get("/api/v1/ca/services")
    assert len(response.json()) == 1

    # Update
    response = client.patch(
        f"/api/v1/ca/services/{svc_id}", params={"name": "Tax Audit"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Tax Audit"

    # Delete
    response = client.delete(f"/api/v1/ca/services/{svc_id}")
    assert response.status_code == 200

    response = client.get("/api/v1/ca/services")
    assert len(response.json()) == 0
