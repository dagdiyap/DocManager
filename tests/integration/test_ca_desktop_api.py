import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
from unittest.mock import patch

from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import models, database, dependencies

# Setup test database
TEST_DB_PATH = Path("test_ca_desktop.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

if TEST_DB_PATH.exists():
    TEST_DB_PATH.unlink()

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Mock user for auth override
fake_ca = models.User(
    id=1, username="test-ca", email="ca@test.com", password_hash="hashed"
)


async def override_get_current_ca(db: Session = Depends(override_get_db)):
    user = db.query(models.User).filter(models.User.id == 1).first()
    return user


async def override_get_current_user_data():
    return {"user_id": 1, "user_type": "ca"}


app.dependency_overrides[database.get_db] = override_get_db
app.dependency_overrides[dependencies.get_current_ca] = override_get_current_ca
app.dependency_overrides[dependencies.get_current_user_data] = (
    override_get_current_user_data
)



@pytest.fixture(scope="module")
def client():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    db.add(fake_ca)
    db.commit()
    db.close()

    app.dependency_overrides[database.get_db] = override_get_db
    app.dependency_overrides[dependencies.get_current_ca] = override_get_current_ca
    app.dependency_overrides[dependencies.get_current_user_data] = override_get_current_user_data

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.pop(database.get_db, None)
    app.dependency_overrides.pop(dependencies.get_current_ca, None)
    app.dependency_overrides.pop(dependencies.get_current_user_data, None)
    models.Base.metadata.drop_all(bind=engine)
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


def test_ca_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "CA Desktop Backend" in response.json()["status"]


def test_client_management(client):
    # 1. Create Client
    client_data = {"phone_number": "1234567890", "name": "Test Client", "email": "client@test.com", "password": "test123"}
    response = client.post("/api/v1/clients/", json=client_data)
    assert response.status_code == 201
    data = response.json()
    
    # Verify response structure
    assert "client" in data
    assert "invite" in data
    assert data["client"]["phone_number"] == "1234567890"
    
    # Verify invite data
    assert data["invite"]["portal_url"]
    assert data["invite"]["username"] == "1234567890"
    assert data["invite"]["password"]  # Password is auto-generated
    assert data["invite"]["qr_code_base64"].startswith("data:image/png;base64,")
    assert data["invite"]["whatsapp_share_url"].startswith("https://wa.me/?text=")

    # 2. List Clients
    response = client.get("/api/v1/clients/")
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_documents_list_empty(client):
    response = client.get("/api/v1/documents/")
    assert response.status_code == 200
    assert response.json() == []
