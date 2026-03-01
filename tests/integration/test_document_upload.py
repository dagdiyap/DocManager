import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from ca_desktop.backend.src.main import app
from ca_desktop.backend.src.database import get_db


@pytest.fixture
def mock_db():
    db = MagicMock()

    def side_effect_refresh(obj):
        obj.id = 1

    db.refresh.side_effect = side_effect_refresh
    return db


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    # Mock auth to return CA user
    from ca_desktop.backend.src.dependencies import get_current_user_data

    app.dependency_overrides[get_current_user_data] = lambda: {
        "user_id": 1,
        "user_type": "ca",
    }

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = {}


@pytest.fixture
def tmp_docs_root(tmp_path):
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.documents_root = tmp_path
        # We also need to mock max_file_size_bytes etc if used
        yield tmp_path


def test_upload_document_success(client, mock_db, tmp_docs_root):
    # Prepare
    file_content = b"test content"
    files = {"file": ("test_doc.pdf", file_content, "application/pdf")}
    data = {"client_phone": "9876543210", "year": "2024"}

    # Mock DB query to return None (new doc)
    mock_db.query.return_value.filter.return_value.first.return_value = None

    # Execute
    response = client.post("/api/v1/documents/upload", files=files, data=data)

    # Assert
    assert response.status_code == 201
    assert response.json()["file_name"] == "test_doc.pdf"

    # Check file saved
    saved_path = tmp_docs_root / "9876543210" / "2024" / "test_doc.pdf"
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content

    # Check DB called
    assert mock_db.add.called
    assert mock_db.commit.called


def test_upload_invalid_extension(client, tmp_docs_root):
    file_content = b"content"
    files = {"file": ("malicious.exe", file_content, "application/octet-stream")}
    data = {"client_phone": "9876543210", "year": "2024"}

    response = client.post("/api/v1/documents/upload", files=files, data=data)

    assert response.status_code == 400
    assert "extension" in response.json()["detail"]


def test_upload_invalid_phone(client, tmp_docs_root):
    file_content = b"content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    data = {"client_phone": "invalid", "year": "2024"}

    response = client.post("/api/v1/documents/upload", files=files, data=data)

    assert response.status_code == 400


def test_upload_overwrite_existing(client, mock_db, tmp_docs_root):
    # Prepare existing file
    mock_doc = MagicMock()
    mock_doc.id = 10
    mock_doc.file_name = "existing.pdf"
    mock_doc.uploaded_at = datetime.utcnow()
    mock_doc.is_deleted = False
    mock_doc.client_phone = "9876543210"
    mock_doc.year = "2024"
    mock_doc.document_type = "existing"

    mock_db.query.return_value.filter.return_value.first.return_value = mock_doc

    file_content = b"updated content"
    files = {"file": ("existing.pdf", file_content, "application/pdf")}
    data = {"client_phone": "9876543210", "year": "2024"}

    response = client.post("/api/v1/documents/upload", files=files, data=data)

    assert response.status_code == 201
    # Check updated fields
    assert mock_doc.file_size == len(file_content)
    assert mock_db.commit.called
