"""Integration tests for client invite system."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ca_desktop.backend.src.database import Base, get_db
from ca_desktop.backend.src.dependencies import get_current_ca, get_password_hash
from ca_desktop.backend.src.main import app
from ca_desktop.backend.src.models import User

# Test database setup
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables at module level
Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override get_db for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_current_ca():
    """Mock CA user for testing."""
    db = TestingSessionLocal()
    ca_user = db.query(User).filter(User.username == "test_ca").first()
    if not ca_user:
        ca_user = User(
            username="test_ca",
            email="ca@test.com",
            password_hash=get_password_hash("test123"),
            display_name="Test CA Firm",
            slug="test-ca-firm",
        )
        db.add(ca_user)
        db.commit()
        db.refresh(ca_user)
    return ca_user


@pytest.fixture(scope="function")
def db_session():
    """Provide a test database session."""
    db = TestingSessionLocal()
    yield db
    # Cleanup
    db.query(User).delete()
    db.commit()
    db.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Provide a test client with overridden dependencies."""
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_ca] = override_get_current_ca
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


class TestClientInviteSystem:
    """Test client invite system functionality."""

    def test_create_client_returns_invite_data(self, client):
        """Test that creating a client returns complete invite data."""
        client_data = {
            "phone_number": "9876543210",
            "name": "Test Client",
            "email": "client@test.com",
            "client_type": "Salaried",
        }
        
        response = client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Verify response structure
        assert "client" in data
        assert "invite" in data
        
        # Verify client data
        assert data["client"]["phone_number"] == "9876543210"
        assert data["client"]["name"] == "Test Client"
        assert data["client"]["email"] == "client@test.com"
        
        # Verify invite data
        invite = data["invite"]
        assert "portal_url" in invite
        assert "username" in invite
        assert "password" in invite
        assert "qr_code_base64" in invite
        assert "whatsapp_share_url" in invite
        
        # Verify invite data format
        assert invite["username"] == "9876543210"
        assert len(invite["password"]) >= 12  # Auto-generated password
        assert invite["qr_code_base64"].startswith("data:image/png;base64,")
        assert invite["whatsapp_share_url"].startswith("https://wa.me/?text=")
        assert "test-ca-firm" in invite["portal_url"]

    def test_create_client_without_email(self, client):
        """Test creating client without email still returns invite data."""
        client_data = {
            "phone_number": "9876543211",
            "name": "Test Client 2",
            "client_type": "Business",
        }
        
        response = client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert "invite" in data
        assert data["invite"]["password"]  # Password still generated
        assert data["invite"]["qr_code_base64"]
        assert data["invite"]["whatsapp_share_url"]

    def test_password_auto_generated(self, client):
        """Test that password is auto-generated when not provided."""
        client_data = {
            "phone_number": "9876543212",
            "name": "Test Client 3",
            "email": "client3@test.com",
            # No password provided - should be auto-generated
        }
        
        response = client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # Password should be auto-generated
        assert data["invite"]["password"]
        assert len(data["invite"]["password"]) >= 12
        
        # Should contain mix of characters
        password = data["invite"]["password"]
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)

    def test_qr_code_contains_portal_url(self, client):
        """Test that QR code is generated for the portal URL."""
        client_data = {
            "phone_number": "9876543213",
            "name": "Test Client 4",
        }
        
        response = client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        # QR code should be base64 encoded PNG
        qr_code = data["invite"]["qr_code_base64"]
        assert qr_code.startswith("data:image/png;base64,")
        
        # Should contain substantial base64 data
        base64_data = qr_code.split(",")[1]
        assert len(base64_data) > 100

    def test_whatsapp_url_contains_credentials(self, client):
        """Test that WhatsApp share URL contains all necessary information."""
        client_data = {
            "phone_number": "9876543214",
            "name": "Test Client 5",
        }
        
        response = client.post("/api/v1/clients/", json=client_data)
        
        assert response.status_code == 201
        data = response.json()
        
        whatsapp_url = data["invite"]["whatsapp_share_url"]
        
        # Should be a valid wa.me URL
        assert whatsapp_url.startswith("https://wa.me/?text=")
        
        # Should contain phone number
        assert "9876543214" in whatsapp_url
        
        # Should contain portal URL reference
        assert "test-ca-firm" in whatsapp_url or "example.com" in whatsapp_url

    def test_duplicate_client_phone_rejected(self, client):
        """Test that duplicate phone numbers are rejected."""
        client_data = {
            "phone_number": "9876543215",
            "name": "Test Client 6",
        }
        
        # Create first client
        response1 = client.post("/api/v1/clients/", json=client_data)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/clients/", json=client_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()


class TestMultiTenantPublicEndpoints:
    """Test multi-tenant public endpoints."""

    def test_get_ca_by_slug(self, client, db_session):
        """Test fetching CA profile by slug."""
        # Create CA user with slug
        ca_user = User(
            username="lokesh",
            email="lokesh@test.com",
            password_hash=get_password_hash("test123"),
            display_name="Lokesh Dagdiya",
            slug="lokesh-dagdiya",
        )
        db_session.add(ca_user)
        db_session.commit()
        
        response = client.get("/api/v1/public/ca-slug/lokesh-dagdiya")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["slug"] == "lokesh-dagdiya"
        assert data["display_name"] == "Lokesh Dagdiya"
        assert data["username"] == "lokesh"

    def test_get_ca_portal_metadata(self, client, db_session):
        """Test fetching CA portal metadata for client login."""
        ca_user = User(
            username="piyush",
            email="piyush@test.com",
            password_hash=get_password_hash("test123"),
            display_name="Piyush Rathi",
            slug="piyush-rathi",
        )
        db_session.add(ca_user)
        db_session.commit()
        
        response = client.get("/api/v1/public/ca-slug/piyush-rathi/portal")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["slug"] == "piyush-rathi"
        assert data["display_name"] == "Piyush Rathi"
        assert "/ca-piyush-rathi/home" in data["portal_url"]

    def test_get_nonexistent_ca_returns_404(self, client):
        """Test that fetching non-existent CA returns 404."""
        response = client.get("/api/v1/public/ca-slug/nonexistent-ca")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAuditLogging:
    """Test audit logging for critical actions."""

    def test_client_creation_logged(self, client, db_session):
        """Test that client creation is logged in audit table."""
        from ca_desktop.backend.src.models import AuditLog
        
        client_data = {
            "phone_number": "9876543220",
            "name": "Audit Test Client",
        }
        
        # Count audit logs before
        initial_count = db_session.query(AuditLog).count()
        
        response = client.post("/api/v1/clients/", json=client_data)
        assert response.status_code == 201
        
        # Check audit log was created
        final_count = db_session.query(AuditLog).count()
        assert final_count == initial_count + 1
        
        # Verify audit log details
        audit_log = db_session.query(AuditLog).order_by(AuditLog.id.desc()).first()
        assert audit_log.event_type == "client_created"
        assert audit_log.user_type == "ca"
        assert audit_log.user_id == "test_ca"
        assert "9876543220" in audit_log.event_details
