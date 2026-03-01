import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from ca_desktop.backend.src.main import app
from ca_desktop.backend.src import models
from ca_desktop.backend.src.database import get_db


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def client(mock_db):
    app.dependency_overrides[get_db] = lambda: mock_db
    # Mock auth to return Client user
    from ca_desktop.backend.src.dependencies import get_current_user_data

    app.dependency_overrides[get_current_user_data] = lambda: {
        "user_id": 1,
        "user_type": "client",
    }

    with TestClient(app) as c:
        yield c

    app.dependency_overrides = {}


@pytest.fixture
def tmp_docs_root(tmp_path):
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.documents_root = tmp_path
        mock_settings.return_value.secret_key = (
            "test_secret_key_must_be_at_least_32_chars_long"
        )
        mock_settings.return_value.token_expiry_seconds = 600
        yield tmp_path


def test_download_audit_logging(client, mock_db, tmp_docs_root):
    # 1. Setup mock document in DB
    client_phone = "9876543210"
    file_name = "test.pdf"

    mock_doc = MagicMock(
        id=1,
        client_phone=client_phone,
        file_path=f"{client_phone}/2024/{file_name}",
        file_name=file_name,
        is_deleted=False,
    )

    mock_client = MagicMock()
    mock_client.phone_number = client_phone

    # Configure mock DB responses
    # Query 1: Get Doc for Token (get_download_token)
    # Query 2: Get Client (get_download_token permission)
    # Query 3: Check Download used (download_file)
    # Query 4: Get Doc (download_file)
    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_doc,  # get_download_token -> doc
        mock_client,  # get_download_token -> client permission
        None,  # download_file -> check if token used (None = not used)
        mock_doc,  # download_file -> get doc
    ]

    # 2. Setup physical file
    file_path = tmp_docs_root / client_phone / "2024" / file_name
    file_path.parent.mkdir(parents=True)
    file_path.write_text("file content")

    # 3. Get Download Token
    resp = client.get("/api/v1/documents/download-token/1")
    assert resp.status_code == 200
    token = resp.json()["token"]

    # 4. Download File
    download_resp = client.get(f"/api/v1/documents/download/{token}")
    assert download_resp.status_code == 200
    assert download_resp.content == b"file content"

    # 5. Verify Audit Log Creation
    # mock_db.add should be called with a Download object
    # We can check the arguments to db.add
    # Note: db.add is called for creating Session (auth) too? No, we mocked auth.
    # But it might be called for other things?
    # Let's inspect calls.

    # Find call where arg is Download instance
    download_log = None
    for call in mock_db.add.call_args_list:
        args = call[0]
        if isinstance(args[0], models.Download):
            download_log = args[0]
            break

    assert download_log is not None
    assert download_log.file_id == 1
    assert download_log.download_token == token
    assert download_log.download_type == "document"
    assert download_log.client_phone == client_phone


def test_single_use_token_enforcement(client, mock_db, tmp_docs_root):
    # Simulate token already used
    client_phone = "9876543210"
    file_name = "test.pdf"
    file_path_str = f"{client_phone}/2024/{file_name}"

    # Create a valid token manually
    from shared.crypto import create_download_token

    token = create_download_token(
        client_phone, file_path_str, "test_secret_key_must_be_at_least_32_chars_long"
    )

    # Setup mock DB to return a Download record when checking token
    mock_existing_download = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = (
        mock_existing_download
    )

    # Attempt download
    resp = client.get(f"/api/v1/documents/download/{token}")

    # Should be forbidden
    assert resp.status_code == 403
    assert "already used" in resp.json()["detail"]
