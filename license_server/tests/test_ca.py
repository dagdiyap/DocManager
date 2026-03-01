"""Tests for CA registration and management."""

import pytest
from fastapi.testclient import TestClient
from license_server.src.database import Base, get_db
from license_server.src.main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Setup Test Database (SQLite in memory for faster unit tests)
SQLALCHEMY_DATABASE_URL = "sqlite://"

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


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_ca():
    """Test successful CA registration."""
    response = client.post(
        "/api/v1/ca/",
        json={
            "id": "CA-001",
            "email": "test@ca.com",
            "name": "Test CA",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "CA-001"
    assert data["email"] == "test@ca.com"
    assert data["is_active"] is True


def test_register_ca_duplicate():
    """Test registration with existing ID."""
    client.post(
        "/api/v1/ca/", json={"id": "CA-001", "email": "test@ca.com", "name": "Test CA"}
    )
    response = client.post(
        "/api/v1/ca/",
        json={"id": "CA-001", "email": "test2@ca.com", "name": "Other CA"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_ca():
    """Test fetching CA by ID."""
    client.post(
        "/api/v1/ca/", json={"id": "CA-001", "email": "test@ca.com", "name": "Test CA"}
    )
    response = client.get("/api/v1/ca/CA-001")
    assert response.status_code == 200
    assert response.json()["name"] == "Test CA"


def test_list_cas():
    """Test listing all CAs."""
    client.post("/api/v1/ca/", json={"id": "CA-1", "email": "1@ca.com", "name": "A"})
    client.post("/api/v1/ca/", json={"id": "CA-2", "email": "2@ca.com", "name": "B"})

    response = client.get("/api/v1/ca/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_ca():
    """Test updating CA information."""
    client.post(
        "/api/v1/ca/", json={"id": "CA-1", "email": "1@ca.com", "name": "Old Name"}
    )
    response = client.patch("/api/v1/ca/CA-1", json={"name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
