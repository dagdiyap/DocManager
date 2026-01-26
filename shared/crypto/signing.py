"""JWT signing and verification for license tokens."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization


class TokenValidationError(Exception):
    """Raised when token validation fails."""

    pass


def create_license_token(
    ca_id: str,
    device_id: str,
    private_key_pem: bytes,
    expiry_days: int = 30,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a signed license token.
    
    Args:
        ca_id: CA identifier
        device_id: Device fingerprint hash
        private_key_pem: RSA private key in PEM format
        expiry_days: Number of days until token expires
        additional_claims: Optional additional JWT claims
        
    Returns:
        Signed JWT token string
    """
    now = datetime.utcnow()
    expiry = now + timedelta(days=expiry_days)

    payload = {
        "ca_id": ca_id,
        "device_id": device_id,
        "issued_at": now.isoformat(),
        "expires_at": expiry.isoformat(),
        "iat": now,
        "exp": expiry,
    }

    if additional_claims:
        payload.update(additional_claims)

    # Load private key
    private_key = serialization.load_pem_private_key(
        private_key_pem, password=None, backend=default_backend()
    )

    # Sign token with RS256
    token = jwt.encode(payload, private_key, algorithm="RS256")

    return token


def verify_license_token(
    token: str, public_key_pem: bytes, expected_device_id: Optional[str] = None
) -> Dict[str, Any]:
    """Verify and decode a license token.
    
    Args:
        token: JWT token string
        public_key_pem: RSA public key in PEM format
        expected_device_id: Optional device ID to verify against
        
    Returns:
        Decoded token payload
        
    Raises:
        TokenValidationError: If token is invalid or expired
    """
    try:
        # Load public key
        public_key = serialization.load_pem_public_key(
            public_key_pem, backend=default_backend()
        )

        # Decode and verify token
        payload = jwt.decode(token, public_key, algorithms=["RS256"])

        # Verify device ID if provided
        if expected_device_id and payload.get("device_id") != expected_device_id:
            raise TokenValidationError(
                f"Device ID mismatch. Expected: {expected_device_id}, "
                f"Got: {payload.get('device_id')}"
            )

        # Check expiry manually (JW SDK also checks, but we want custom error)
        expires_at = datetime.fromisoformat(payload["expires_at"])
        if datetime.utcnow() > expires_at:
            raise TokenValidationError(f"Token expired at {expires_at}")

        return payload

    except jwt.ExpiredSignatureError as e:
        raise TokenValidationError("Token has expired") from e
    except jwt.InvalidTokenError as e:
        raise TokenValidationError(f"Invalid token: {str(e)}") from e
    except Exception as e:
        raise TokenValidationError(f"Token validation failed: {str(e)}") from e


def decode_token_without_verification(token: str) -> Dict[str, Any]:
    """Decode token without verifying signature (for debugging).
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Warning:
        This does not verify the token signature! Only use for debugging.
    """
    return jwt.decode(token, options={"verify_signature": False})


def get_token_expiry(token: str) -> datetime:
    """Get token expiration time without full verification.
    
    Args:
        token: JWT token string
        
    Returns:
        Token expiration datetime
    """
    payload = decode_token_without_verification(token)
    return datetime.fromisoformat(payload["expires_at"])


def is_token_expired(token: str) -> bool:
    """Check if token is expired without full verification.
    
    Args:
        token: JWT token string
        
    Returns:
        True if token is expired
    """
    try:
        expiry = get_token_expiry(token)
        return datetime.utcnow() > expiry
    except Exception:
        return True  # If we can't decode, consider it expired
