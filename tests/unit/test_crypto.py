import pytest
from shared.crypto.keys import generate_rsa_keypair, RSAKeyManager
from shared.crypto.tokens import (
    create_download_token,
    verify_download_token,
    DownloadTokenError,
)
from datetime import datetime


def test_rsa_key_generation():
    """Verify manual keypair generation works."""
    priv, pub = generate_rsa_keypair(key_size=2048)
    assert b"BEGIN PRIVATE KEY" in priv
    assert b"BEGIN PUBLIC KEY" in pub


def test_rsa_key_manager(tmp_path):
    """Verify RSAKeyManager saves and loads keys correctly."""
    key_dir = tmp_path / "keys"
    manager = RSAKeyManager(key_dir)
    priv, pub = manager.generate_keypair()

    assert (key_dir / "private_key.pem").exists()
    assert (key_dir / "public_key.pem").exists()

    assert manager.load_private_key() == priv
    assert manager.load_public_key() == pub


def test_download_token_cycle():
    """Verify creation and verification of download tokens."""
    secret = "test-secret"
    phone = "9876543210"
    file_path = "/tmp/docs/test.pdf"

    token = create_download_token(phone, file_path, secret, expiry_seconds=60)
    data = verify_download_token(token, secret)

    assert data.client_phone == phone
    assert data.file_path == file_path
    assert data.expiry > datetime.utcnow()


def test_download_token_invalid_secret():
    """Verify token fails with wrong secret."""
    secret = "correct-secret"
    phone = "9876543210"
    file_path = "/tmp/docs/test.pdf"

    token = create_download_token(phone, file_path, secret)

    with pytest.raises(DownloadTokenError, match="Invalid token signature"):
        verify_download_token(token, "wrong-secret")


def test_download_token_expired():
    """Verify token fails when expired."""
    secret = "test-secret"
    phone = "9876543210"
    file_path = "/tmp/docs/test.pdf"

    # Create token with -1 expiry
    token = create_download_token(phone, file_path, secret, expiry_seconds=-10)

    with pytest.raises(DownloadTokenError, match="Token expired"):
        verify_download_token(token, secret)
