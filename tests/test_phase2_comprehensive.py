"""
Comprehensive CA Backend & Integration Tests

Tests all Phase 2 features including:
- Document tagging and management
- Compliance checking
- Reminder system
- CA profile management
- Public API access
- Complete workflows
"""

import pytest
from datetime import datetime, timedelta

from ca_desktop.backend.src import database as _database
from sqlalchemy import text

from ca_desktop.backend.src.database import init_db, Base
from ca_desktop.backend.src.models import (
    User,
    Client,
    Document,
    DocumentTag,
    ComplianceRule,
    Reminder,
    CAProfile,
    CAMediaItem,
    Service,
    Testimonial,
)
from ca_desktop.backend.src.config import get_settings
from ca_desktop.backend.src.dependencies import get_password_hash


# ============ FIXTURES ============


@pytest.fixture(scope="session")
def setup_database():
    """Setup test database with all tables."""
    _ = get_settings()  # ensure settings loaded

    # Create all tables
    init_db()

    # Seed default tags
    db = _database.SessionLocal()

    default_tags = [
        ("ITR", "Income Tax Return", r"ITR|Income Tax Return|income tax"),
        ("Form 16", "Salary Certificate", r"Form 16|Form16|F16|salary certificate"),
        ("Bank Statement", "Bank Account Statement", r"Bank|Statement|bank statement"),
        ("GST Return", "Goods & Services Tax Return", r"GST|GSTR|Return|gst return"),
        ("Notice", "Tax Notice or Order", r"Notice|Order|notice|order"),
        ("Audit Report", "Statutory Audit Certificate", r"Audit|Report|audit report"),
    ]

    for name, desc, pattern in default_tags:
        existing = db.query(DocumentTag).filter(DocumentTag.name == name).first()
        if not existing:
            tag = DocumentTag(name=name, description=desc, regex_pattern=pattern)
            db.add(tag)

    # Seed compliance rules
    compliance_rules = [
        {
            "name": "Salaried Employee Compliance",
            "client_type": "Salaried",
            "required_document_tags": ["ITR", "Form 16", "Bank Statement"],
        },
        {
            "name": "Business Owner Compliance",
            "client_type": "Business",
            "required_document_tags": ["ITR", "GST Return", "Audit Report"],
        },
        {
            "name": "Partnership Compliance",
            "client_type": "Partnership",
            "required_document_tags": ["ITR", "GST Return", "Audit Report"],
        },
    ]

    for rule in compliance_rules:
        existing = (
            db.query(ComplianceRule)
            .filter(ComplianceRule.client_type == rule["client_type"])
            .first()
        )
        if not existing:
            cr = ComplianceRule(**rule)
            db.add(cr)

    db.commit()
    db.close()

    yield

    # Cleanup - drop all tables after tests
    Base.metadata.drop_all(bind=_database.engine)


@pytest.fixture
def db_session(setup_database):
    """Create a new database session for each test."""
    session = _database.SessionLocal()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def test_ca_user(db_session):
    """Create a test CA user."""
    db_session.query(Testimonial).delete()
    db_session.query(Service).delete()
    db_session.query(CAMediaItem).delete()
    db_session.query(CAProfile).delete()
    db_session.query(Reminder).delete()
    db_session.execute(text("DELETE FROM document_document_tag"))
    db_session.query(Document).delete()
    db_session.query(Client).delete()
    db_session.query(User).filter(User.username == "test_ca").delete()
    db_session.commit()

    ca = User(
        username="test_ca",
        email="ca@test.com",
        password_hash=get_password_hash("password123"),
    )
    db_session.add(ca)
    db_session.commit()
    db_session.refresh(ca)
    yield ca
    db_session.query(Testimonial).delete()
    db_session.query(Service).delete()
    db_session.query(CAMediaItem).delete()
    db_session.query(CAProfile).delete()
    db_session.query(Reminder).delete()
    db_session.execute(text("DELETE FROM document_document_tag"))
    db_session.query(Document).delete()
    db_session.query(Client).delete()
    db_session.query(User).filter(User.username == "test_ca").delete()
    db_session.commit()


@pytest.fixture
def test_clients(db_session):
    """Create 3 test clients with different types."""
    clients = []

    client_data = [
        ("9876543210", "Amit Sharma", "Salaried"),
        ("9876543211", "Priya Enterprises", "Business"),
        ("9876543212", "ABC Partnership", "Partnership"),
    ]

    for phone, name, client_type in client_data:
        client = Client(
            phone_number=phone,
            name=name,
            client_type=client_type,
            password_hash=get_password_hash("client123"),
            email=f"{phone}@example.com",
        )
        db_session.add(client)
        clients.append(client)

    db_session.commit()
    for client in clients:
        db_session.refresh(client)

    yield clients

    phones = ["9876543210", "9876543211", "9876543212"]
    db_session.query(Client).filter(Client.phone_number.in_(phones)).delete(synchronize_session=False)
    db_session.query(User).filter(User.username == "test_ca").delete()
    db_session.commit()


@pytest.fixture
def test_documents(db_session, test_clients):
    """Create test documents for clients."""
    documents = []
    client = test_clients[0]

    doc_data = [
        ("ITR.pdf", "ITR", "2024-25", 250000),
        ("Form16.xlsx", "Form 16", "2024-25", 150000),
        ("BankStatement.pdf", "Bank Statement", "2024-25", 400000),
    ]

    for filename, doc_type, year, size in doc_data:
        doc = Document(
            client_phone=client.phone_number,
            year=year,
            document_type=doc_type,
            file_name=filename,
            file_path=f"documents/{client.phone_number}/{year}/{filename}",
            file_size=size,
            is_deleted=False,
        )
        db_session.add(doc)
        documents.append(doc)

    db_session.commit()
    for doc in documents:
        db_session.refresh(doc)

    yield documents

    from sqlalchemy import text
    db_session.execute(text("DELETE FROM document_document_tag"))
    db_session.query(Document).filter(
        Document.client_phone == client.phone_number
    ).delete(synchronize_session=False)
    db_session.commit()


# ============ UNIT TESTS ============


class TestDocumentTagging:
    """Test document tagging functionality."""

    def test_tag_creation(self, db_session):
        """Test creating document tags."""
        tags = db_session.query(DocumentTag).all()
        assert len(tags) == 6
        assert any(t.name == "ITR" for t in tags)

    def test_document_tag_relationship(self, db_session, test_documents):
        """Test adding tags to documents."""
        doc = test_documents[0]
        itr_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "ITR").first()
        )

        doc.tags.append(itr_tag)
        db_session.commit()

        db_session.refresh(doc)
        assert itr_tag in doc.tags

    def test_multiple_tags_per_document(self, db_session, test_documents):
        """Test adding multiple tags to one document."""
        doc = test_documents[0]
        itr_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "ITR").first()
        )
        notice_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "Notice").first()
        )

        doc.tags.append(itr_tag)
        doc.tags.append(notice_tag)
        db_session.commit()

        db_session.refresh(doc)
        assert len(doc.tags) == 2


class TestCompliance:
    """Test compliance checking functionality."""

    def test_compliance_rule_exists(self, db_session):
        """Test that compliance rules are created."""
        rules = db_session.query(ComplianceRule).all()
        assert len(rules) == 3
        assert any(r.client_type == "Salaried" for r in rules)

    def test_compliance_required_documents(self, db_session):
        """Test compliance rule required documents."""
        rule = (
            db_session.query(ComplianceRule)
            .filter(ComplianceRule.client_type == "Salaried")
            .first()
        )

        assert rule is not None
        assert "ITR" in rule.required_document_tags
        assert "Form 16" in rule.required_document_tags
        assert "Bank Statement" in rule.required_document_tags

    def test_client_type_assignment(self, db_session, test_clients):
        """Test assigning client type."""
        client = test_clients[0]
        assert client.client_type == "Salaried"

        client2 = test_clients[1]
        assert client2.client_type == "Business"


class TestReminders:
    """Test reminder system."""

    def test_create_reminder(self, db_session, test_clients, test_ca_user):
        """Test creating a reminder."""
        client = test_clients[0]
        tag = db_session.query(DocumentTag).filter(DocumentTag.name == "ITR").first()

        reminder = Reminder(
            client_phone=client.phone_number,
            reminder_type="document_type",
            tag_id=tag.id,
            reminder_date=datetime.utcnow() + timedelta(days=7),
            message="Please arrange ITR documents",
            created_by_ca_id=test_ca_user.id,
        )

        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)

        assert reminder.id is not None
        assert reminder.client_phone == client.phone_number

    def test_recurring_reminder(self, db_session, test_clients, test_ca_user):
        """Test creating recurring reminder."""
        client = test_clients[0]
        tag = (
            db_session.query(DocumentTag)
            .filter(DocumentTag.name == "GST Return")
            .first()
        )

        reminder = Reminder(
            client_phone=client.phone_number,
            reminder_type="document_type",
            tag_id=tag.id,
            reminder_date=datetime.utcnow() + timedelta(days=30),
            is_recurring=True,
            recurrence_pattern="monthly",
            message="Monthly GST return due",
            created_by_ca_id=test_ca_user.id,
        )

        db_session.add(reminder)
        db_session.commit()
        db_session.refresh(reminder)

        assert reminder.is_recurring is True
        assert reminder.recurrence_pattern == "monthly"


class TestCAProfile:
    """Test CA profile management."""

    def test_create_ca_profile(self, db_session, test_ca_user):
        """Test creating CA profile."""
        profile = CAProfile(
            ca_id=test_ca_user.id,
            firm_name="Sharma Chartered Accountants",
            professional_bio="Expert in tax and GST",
            address="123 Main Street, Delhi",
            phone_number="+91-9999999999",
            email="ca@example.com",
        )

        db_session.add(profile)
        db_session.commit()
        db_session.refresh(profile)

        assert profile.firm_name == "Sharma Chartered Accountants"
        assert profile.ca_id == test_ca_user.id

    def test_ca_media_items(self, db_session, test_ca_user):
        """Test adding media items to CA profile."""
        media1 = CAMediaItem(
            ca_id=test_ca_user.id,
            item_type="carousel",
            file_path="uploads/ca_1/carousel/photo1.jpg",
            title="Office Building",
            order_index=0,
            is_active=True,
        )

        media2 = CAMediaItem(
            ca_id=test_ca_user.id,
            item_type="carousel",
            file_path="uploads/ca_1/carousel/photo2.jpg",
            title="Team Photo",
            order_index=1,
            is_active=True,
        )

        db_session.add_all([media1, media2])
        db_session.commit()

        media_items = (
            db_session.query(CAMediaItem)
            .filter(CAMediaItem.ca_id == test_ca_user.id)
            .all()
        )

        assert len(media_items) == 2

    def test_services(self, db_session, test_ca_user):
        """Test CA services."""
        service = Service(
            ca_id=test_ca_user.id,
            name="ITR Filing",
            description="Complete ITR filing service",
            order_index=0,
        )

        db_session.add(service)
        db_session.commit()
        db_session.refresh(service)

        assert service.name == "ITR Filing"

    def test_testimonials(self, db_session, test_ca_user):
        """Test CA testimonials."""
        testimonial = Testimonial(
            ca_id=test_ca_user.id,
            client_name="John Doe",
            text="Excellent service!",
            rating=5,
        )

        db_session.add(testimonial)
        db_session.commit()
        db_session.refresh(testimonial)

        assert testimonial.rating == 5
        assert testimonial.client_name == "John Doe"


# ============ INTEGRATION TESTS ============


class TestCompleteWorkflows:
    """Test complete workflows combining multiple features."""

    def test_salaried_client_compliance_workflow(
        self, db_session, test_clients, test_ca_user
    ):
        """Test complete salaried client compliance workflow."""
        client = test_clients[0]

        # Get compliance rule
        rule = (
            db_session.query(ComplianceRule)
            .filter(ComplianceRule.client_type == "Salaried")
            .first()
        )

        assert rule is not None

        # Create documents
        itr_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "ITR").first()
        )
        form16_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "Form 16").first()
        )

        # Upload ITR
        doc1 = Document(
            client_phone=client.phone_number,
            year="2024-25",
            document_type="ITR",
            file_name="ITR_2024.pdf",
            file_path=f"documents/{client.phone_number}/2024-25/ITR_2024.pdf",
            file_size=250000,
        )
        doc1.tags.append(itr_tag)
        db_session.add(doc1)

        # Upload Form 16
        doc2 = Document(
            client_phone=client.phone_number,
            year="2024-25",
            document_type="Form 16",
            file_name="Form16.xlsx",
            file_path=f"documents/{client.phone_number}/2024-25/Form16.xlsx",
            file_size=150000,
        )
        doc2.tags.append(form16_tag)
        db_session.add(doc2)

        db_session.commit()

        # Check client documents
        client_docs = (
            db_session.query(Document)
            .filter(
                Document.client_phone == client.phone_number, Document.year == "2024-25"
            )
            .all()
        )

        assert len(client_docs) == 2

        # Create reminder for missing Bank Statement
        bank_tag = (
            db_session.query(DocumentTag)
            .filter(DocumentTag.name == "Bank Statement")
            .first()
        )

        reminder = Reminder(
            client_phone=client.phone_number,
            reminder_type="document_type",
            tag_id=bank_tag.id,
            reminder_date=datetime.utcnow() + timedelta(days=7),
            message="Please provide Bank Statement",
            created_by_ca_id=test_ca_user.id,
        )
        db_session.add(reminder)
        db_session.commit()

        # Verify reminder created
        reminders = (
            db_session.query(Reminder)
            .filter(Reminder.client_phone == client.phone_number)
            .all()
        )
        assert len(reminders) == 1

    def test_business_client_full_setup(self, db_session, test_clients, test_ca_user):
        """Test complete business client setup with all documents and reminders."""
        client = test_clients[1]

        # Get all required tags
        itr_tag = (
            db_session.query(DocumentTag).filter(DocumentTag.name == "ITR").first()
        )
        gst_tag = (
            db_session.query(DocumentTag)
            .filter(DocumentTag.name == "GST Return")
            .first()
        )
        audit_tag = (
            db_session.query(DocumentTag)
            .filter(DocumentTag.name == "Audit Report")
            .first()
        )

        # Create all required documents
        docs_data = [
            ("ITR_2024.pdf", "ITR", itr_tag, 300000),
            ("GST_Return_2024.xlsx", "GST Return", gst_tag, 200000),
            ("Audit_Report_2024.pdf", "Audit Report", audit_tag, 500000),
        ]

        for filename, doc_type, tag, size in docs_data:
            doc = Document(
                client_phone=client.phone_number,
                year="2024-25",
                document_type=doc_type,
                file_name=filename,
                file_path=f"documents/{client.phone_number}/2024-25/{filename}",
                file_size=size,
            )
            doc.tags.append(tag)
            db_session.add(doc)

        db_session.commit()

        # Verify all documents
        docs = (
            db_session.query(Document)
            .filter(Document.client_phone == client.phone_number)
            .all()
        )
        assert len(docs) == 3

        # Verify all tags assigned
        for doc in docs:
            assert len(doc.tags) > 0

    def test_ca_profile_complete_setup(self, db_session, test_ca_user):
        """Test complete CA profile setup."""
        # Create profile
        profile = CAProfile(
            ca_id=test_ca_user.id,
            firm_name="Sharma & Associates",
            professional_bio="Expert CAs",
            address="Delhi, India",
            phone_number="+91-9999999999",
            email="ca@example.com",
            website_url="https://example.com",
            linkedin_url="https://linkedin.com/in/example",
        )
        db_session.add(profile)

        # Add media
        for i in range(3):
            media = CAMediaItem(
                ca_id=test_ca_user.id,
                item_type="carousel",
                file_path=f"uploads/{test_ca_user.id}/carousel/photo{i}.jpg",
                title=f"Photo {i + 1}",
                order_index=i,
                is_active=True,
            )
            db_session.add(media)

        # Add services
        services_data = ["ITR Filing", "GST Registration", "Audit Services"]
        for i, service_name in enumerate(services_data):
            service = Service(
                ca_id=test_ca_user.id,
                name=service_name,
                description=f"Complete {service_name} service",
                order_index=i,
            )
            db_session.add(service)

        # Add testimonials
        testimonials_data = [
            ("Amit Kumar", "Excellent service!"),
            ("Priya Singh", "Very professional"),
            ("Rahul Patel", "Highly recommended"),
        ]
        for client_name, text in testimonials_data:
            testimonial = Testimonial(
                ca_id=test_ca_user.id, client_name=client_name, text=text, rating=5
            )
            db_session.add(testimonial)

        db_session.commit()

        # Verify all data
        profile = (
            db_session.query(CAProfile)
            .filter(CAProfile.ca_id == test_ca_user.id)
            .first()
        )
        assert profile.firm_name == "Sharma & Associates"

        media = (
            db_session.query(CAMediaItem)
            .filter(CAMediaItem.ca_id == test_ca_user.id)
            .all()
        )
        assert len(media) == 3

        services = (
            db_session.query(Service).filter(Service.ca_id == test_ca_user.id).all()
        )
        assert len(services) == 3

        testimonials = (
            db_session.query(Testimonial)
            .filter(Testimonial.ca_id == test_ca_user.id)
            .all()
        )
        assert len(testimonials) == 3


# ============ RUN TESTS ============

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
