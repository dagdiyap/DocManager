import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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


def seed_data(db):
    db.query(models.ComplianceRule).delete()
    db.execute(text("DELETE FROM document_document_tag"))
    db.query(models.Document).delete()
    db.query(models.DocumentTag).delete()
    db.query(models.Client).delete()
    db.query(models.User).delete()
    db.commit()

    ca = models.User(username="admin", email="admin@test.com", password_hash="hash")
    db.add(ca)
    client = models.Client(
        phone_number="9876543210",
        name="Test Client",
        password_hash="hash",
        client_type="Salaried",
    )
    db.add(client)
    tag1 = models.DocumentTag(name="ITR", regex_pattern="ITR")
    tag2 = models.DocumentTag(name="Form 16", regex_pattern="Form 16")
    db.add(tag1)
    db.add(tag2)
    rule = models.ComplianceRule(
        name="Salaried Rules",
        client_type="Salaried",
        required_document_tags=["ITR", "Form 16"],
    )
    db.add(rule)
    db.commit()
    return client


def test_compliance_status_missing_all(client, db_session):
    seed_data(db_session)

    response = client.get("/api/v1/clients/9876543210/compliance")
    assert response.status_code == 200
    data = response.json()

    assert data["is_compliant"] is False
    assert data["missing_count"] == 2
    assert len(data["missing_documents"]) == 2

    missing_tags = [m["tag"] for m in data["missing_documents"]]
    assert "ITR" in missing_tags
    assert "Form 16" in missing_tags


def test_compliance_status_partial(client, db_session):
    seed_data(db_session)

    # Add ITR document
    tag_itr = db_session.query(models.DocumentTag).filter_by(name="ITR").first()
    doc = models.Document(
        client_phone="9876543210",
        year="2024",
        document_type="ITR",
        file_name="ITR.pdf",
        file_path="path/to/ITR.pdf",
        is_deleted=False,
    )
    doc.tags.append(tag_itr)
    db_session.add(doc)
    db_session.commit()

    response = client.get("/api/v1/clients/9876543210/compliance")
    data = response.json()

    assert data["is_compliant"] is False
    assert data["missing_count"] == 1
    assert data["missing_documents"][0]["tag"] == "Form 16"


def test_compliance_status_fully_compliant(client, db_session):
    seed_data(db_session)

    # Add ITR and Form 16
    tag_itr = db_session.query(models.DocumentTag).filter_by(name="ITR").first()
    tag_f16 = db_session.query(models.DocumentTag).filter_by(name="Form 16").first()

    doc1 = models.Document(
        client_phone="9876543210",
        year="2024",
        document_type="ITR",
        file_name="ITR.pdf",
        file_path="p1",
        is_deleted=False,
    )
    doc1.tags.append(tag_itr)

    doc2 = models.Document(
        client_phone="9876543210",
        year="2024",
        document_type="Form 16",
        file_name="F16.pdf",
        file_path="p2",
        is_deleted=False,
    )
    doc2.tags.append(tag_f16)

    db_session.add_all([doc1, doc2])
    db_session.commit()

    response = client.get("/api/v1/clients/9876543210/compliance")
    data = response.json()

    assert data["is_compliant"] is True
    assert data["missing_count"] == 0
