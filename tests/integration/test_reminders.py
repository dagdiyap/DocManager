import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime, timedelta

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


def seed_reminder_data(db):
    db.query(models.Reminder).delete()
    db.query(models.DocumentTag).delete()
    db.query(models.Client).delete()
    db.query(models.User).delete()
    db.commit()

    ca = models.User(
        id=1, username="admin", email="admin@test.com", password_hash="hash"
    )
    db.add(ca)
    client = models.Client(
        phone_number="9876543210",
        name="Test Client",
        password_hash="hash",
        client_type="Salaried",
    )
    db.add(client)
    tag = models.DocumentTag(name="ITR")
    db.add(tag)
    db.commit()
    return client


def test_create_reminder(client, db_session):
    seed_reminder_data(db_session)

    payload = {
        "reminder_type": "document_type",
        "tag_id": 1,
        "reminder_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "message": "Please upload ITR",
        "is_recurring": False,
    }

    # Note: query param client_phone is required for create_reminder POST
    response = client.post(
        "/api/v1/reminders", params={"client_phone": "9876543210"}, json=payload
    )  # Wait, query params mixed with json?
    # Checking router signature: create_reminder args are mostly query params except maybe body?
    # No, FastAPI separates Body and Query.
    # In `reminders.py`:
    # client_phone: str,
    # reminder_type: str,
    # reminder_date: datetime,
    # ...
    # All are simple types, so they are Query params by default unless Pydantic model is used.
    # Ah, checking code:
    # def create_reminder(client_phone: str, reminder_type: str, ...):
    # They are indeed Query parameters (or Body if configured, but default is Query for simple types in FastAPI if not Path).
    # Wait, usually for POST, simple types might be Body if Body() is used, or Query if Query() is used.
    # If not specified, they are Query params for GET, but for POST?
    # FastAPI convention:
    # - Pydantic model -> Body
    # - singular values -> Query
    # Let's check `reminders.py` again. It doesn't use Pydantic model for input!
    # It uses individual arguments.
    # This is bad practice for POST, but let's test what's implemented.
    # I should fix this to use a Pydantic model in the future, but for "Test Reminder System" I must test AS IS.

    # Let's send as query params.
    params = {
        "client_phone": "9876543210",
        "reminder_type": "document_type",
        "reminder_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
        "tag_id": 1,
        "message": "Please upload ITR",
    }
    response = client.post("/api/v1/reminders", params=params)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Please upload ITR"
    assert data["client_phone"] == "9876543210"


def test_list_reminders(client, db_session):
    seed_reminder_data(db_session)

    # Create a reminder directly in DB
    reminder = models.Reminder(
        client_phone="9876543210",
        reminder_type="custom",
        reminder_date=datetime.utcnow() + timedelta(days=1),
        message="Custom Reminder",
        created_by_ca_id=1,
        created_at=datetime.utcnow(),
    )
    db_session.add(reminder)
    db_session.commit()

    response = client.get("/api/v1/reminders", params={"client_phone": "9876543210"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Custom Reminder"


def test_group_reminders(client, db_session):
    seed_reminder_data(db_session)

    # Add another client
    client2 = models.Client(phone_number="1234567890", name="C2", password_hash="h")
    db_session.add(client2)
    db_session.commit()

    # Both clients missing ITR (tag id 1). Neither has doc.

    params = {
        "filter_type": "missing_documents",
        "tag_id": 1,
        "message": "Group Reminder",
    }
    response = client.post("/api/v1/reminders/send-group", params=params)

    assert response.status_code == 200
    data = response.json()
    assert data["sent_count"] == 2
    assert "9876543210" in data["affected_clients"]
    assert "1234567890" in data["affected_clients"]
