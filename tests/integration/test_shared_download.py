import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from ca_desktop.backend.src.main import app
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
def tmp_shared_root(tmp_path):
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.shared_files_root = tmp_path
        # We need secret key for token generation
        mock_settings.return_value.secret_key = (
            "test_secret_key_must_be_at_least_32_chars_long"
        )
        mock_settings.return_value.token_expiry_seconds = 600
        mock_settings.return_value.documents_root = tmp_path / "docs"  # just in case
        yield tmp_path


def test_shared_file_download_flow(client, mock_db, tmp_shared_root):
    # 1. Setup mock shared file in DB
    client_phone = "9876543210"
    file_name = "shared_doc.pdf"

    mock_client = MagicMock()
    mock_client.phone_number = client_phone

    mock_shared_file = MagicMock(
        id=1,
        client_phone=client_phone,
        file_path=f"{client_phone}/{file_name}",
        file_name=file_name,
    )

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        # 1. Get Token: shared file
        mock_shared_file,
        # 2. Get Token: client (permission)
        mock_client,
        # 3. Download: Check token used (None = not used)
        None,
        # 4. Download: Find shared file
        mock_shared_file,
    ]

    # 2. Setup physical file
    file_path = tmp_shared_root / client_phone / file_name
    file_path.parent.mkdir(parents=True)
    file_path.write_text("shared content")

    # 3. Get Download Token
    resp = client.get("/api/v1/messaging/shared-files/download-token/1")
    assert resp.status_code == 200
    token = resp.json()["token"]

    # 4. Download File
    # Note: The download endpoint uses FileStreamer which uses config settings.
    # Our tmp_shared_root fixture patched settings globally?
    # The patch context manager in fixture only applies during fixture yield.
    # But for the API call inside test function, we need the patch active.
    # The fixture yields 'tmp_path', but the patch is active?
    # Wait, 'yield tmp_path' is inside 'with patch...'. Yes, it is active.

    download_resp = client.get(f"/api/v1/messaging/shared-files/download/{token}")
    assert download_resp.status_code == 200
    assert download_resp.content == b"shared content"


def test_shared_file_access_denied(client, mock_db):
    # Setup mock shared file belonging to OTHER client
    client_phone = "9876543210"
    other_phone = "1234567890"

    mock_file = MagicMock(
        id=1,
        client_phone=other_phone,  # Different phone
        file_path="some/path",
    )

    mock_client = MagicMock()
    mock_client.phone_number = client_phone  # Current user phone

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        mock_file,
        mock_client,
    ]

    resp = client.get("/api/v1/messaging/shared-files/download-token/1")
    assert resp.status_code == 403
