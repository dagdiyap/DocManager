import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ca_desktop.backend.src.database import Base, get_db
from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import models

# Setup in-memory DB for testing
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


@pytest.fixture(autouse=True)
def setup_db():
    yield
    db = TestingSessionLocal()
    db.query(models.User).delete()
    db.commit()
    db.close()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def test_ca_registration_and_login(client):
    # 1. Register CA
    reg_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "securepassword",
    }
    response = client.post("/api/v1/auth/register", json=reg_data)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "admin"
    assert "id" in data

    # 2. Login CA
    login_data = {"username": "admin", "password": "securepassword"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert token_data["user_type"] == "ca"


def test_prevent_duplicate_registration(client):
    # 1. Register first CA
    reg_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "securepassword",
    }
    client.post("/api/v1/auth/register", json=reg_data)

    # 2. Attempt second registration
    reg_data_2 = {
        "username": "admin2",
        "email": "admin2@example.com",
        "password": "password",
    }
    response = client.post("/api/v1/auth/register", json=reg_data_2)

    # Should be forbidden
    assert response.status_code == 403
    assert "already exists" in response.json()["detail"]


def test_login_invalid_credentials(client):
    login_data = {"username": "admin", "password": "wrongpassword"}
    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
