import pytest
from shared.crypto import (
    create_license_token,
    generate_device_fingerprint,
    generate_rsa_keypair,
    verify_license_token,
)


def test_rsa_key_generation():
    private_key, public_key = generate_rsa_keypair()
    assert b"PRIVATE KEY" in private_key
    assert b"PUBLIC KEY" in public_key


def test_license_token_creation_and_verification():
    # 1. Setup keys
    private_key_pem, public_key_pem = generate_rsa_keypair()

    # 2. Data
    ca_id = "CA_TEST_001"
    device_id = generate_device_fingerprint()
    expiry_days = 30

    # 3. Create Token
    token = create_license_token(
        ca_id=ca_id,
        device_id=device_id,
        expiry_days=expiry_days,
        private_key_pem=private_key_pem,
    )

    assert isinstance(token, str)
    assert len(token.split(".")) == 3  # Header, Payload, Signature

    # 4. Verify Token
    payload = verify_license_token(
        token=token, public_key_pem=public_key_pem, expected_device_id=device_id
    )

    assert payload["ca_id"] == ca_id
    assert payload["device_id"] == device_id
    assert "expires_at" in payload


def test_license_token_invalid_device():
    private_key_pem, public_key_pem = generate_rsa_keypair()

    token = create_license_token(
        ca_id="CA_1",
        device_id="DEVICE_A",
        expiry_days=1,
        private_key_pem=private_key_pem,
    )

    with pytest.raises(Exception) as excinfo:
        verify_license_token(token, public_key_pem, expected_device_id="DEVICE_B")
    assert "Device ID mismatch" in str(excinfo.value)


def test_license_token_expired():
    private_key_pem, public_key_pem = generate_rsa_keypair()

    # Expired token (using negative expiry)
    token = create_license_token(
        ca_id="CA_1",
        device_id="DEVICE_A",
        expiry_days=-1,
        private_key_pem=private_key_pem,
    )

    with pytest.raises(Exception) as excinfo:
        verify_license_token(token, public_key_pem, expected_device_id="DEVICE_A")
    assert "expired" in str(excinfo.value).lower()
