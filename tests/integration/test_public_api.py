import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ca_desktop.backend.src.database import Base, get_db
from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import models

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
    yield TestClient(app)


def seed_public_data(db):
    db.query(models.Testimonial).delete()
    db.query(models.Service).delete()
    db.query(models.CAMediaItem).delete()
    db.query(models.CAProfile).delete()
    db.query(models.User).delete()
    db.commit()

    ca = models.User(
        id=1, username="admin", email="admin@test.com", password_hash="hash"
    )
    db.add(ca)

    # Profile
    profile = models.CAProfile(
        ca_id=1,
        firm_name="Public CA Firm",
        professional_bio="Expert Services",
        email="contact@public.com",
        phone_number="1234567890",
        website_url="https://public.com",
    )
    db.add(profile)

    # Media
    media = models.CAMediaItem(
        ca_id=1,
        item_type="carousel",
        file_path="img1.jpg",
        order_index=0,
        is_active=True,
    )
    db.add(media)

    # Service
    service = models.Service(
        ca_id=1,
        name="Tax Audit",
        description="Full audit",
        order_index=0,
        is_active=True,
    )
    db.add(service)

    # Testimonial
    testimonial = models.Testimonial(
        ca_id=1,
        client_name="Happy Client",
        text="Great service",
        rating=5,
        order_index=0,
        is_active=True,
    )
    db.add(testimonial)

    db.commit()


def test_public_profile(client, db_session):
    seed_public_data(db_session)
    response = client.get("/api/v1/public/ca/admin/profile")
    assert response.status_code == 200
    data = response.json()
    assert data["firm_name"] == "Public CA Firm"
    assert "email" in data  # Public profile exposes contact info


def test_public_media(client, db_session):
    seed_public_data(db_session)
    response = client.get("/api/v1/public/ca/admin/media")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["file_path"] == "img1.jpg"


def test_public_services(client, db_session):
    seed_public_data(db_session)
    response = client.get("/api/v1/public/ca/admin/services")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Tax Audit"


def test_public_testimonials(client, db_session):
    seed_public_data(db_session)
    response = client.get("/api/v1/public/ca/admin/testimonials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["client_name"] == "Happy Client"


def test_public_profile_not_found(client, db_session):
    response = client.get("/api/v1/public/ca/unknown_user/profile")
    assert response.status_code == 404
