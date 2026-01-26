"""Download token generation and validation."""

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class DownloadTokenData:
    """Download token payload."""

    client_phone: str
    file_path: str
    expiry: datetime
    nonce: str


class DownloadTokenError(Exception):
    """Raised when download token validation fails."""

    pass


def create_download_token(
    client_phone: str,
    file_path: str,
    secret_key: str,
    expiry_seconds: int = 600,
) -> str:
    """Create HMAC-signed download token.
    
    Args:
        client_phone: Client phone number
        file_path: Full file path
        secret_key: HMAC secret key
        expiry_seconds: Token validity in seconds (default: 10 minutes)
        
    Returns:
        Base64-encoded token string
    """
    # Generate cryptographic nonce
    nonce = secrets.token_hex(16)

    # Calculate expiry time
    expiry = datetime.utcnow() + timedelta(seconds=expiry_seconds)

    # Create payload
    payload = f"{client_phone}|{file_path}|{expiry.isoformat()}|{nonce}"

    # Generate HMAC signature
    signature = hmac.new(
        secret_key.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()

    # Combine payload and signature
    token = f"{payload}|{signature}"

    # Base64 encode for URL safety
    import base64

    token_b64 = base64.urlsafe_b64encode(token.encode()).decode()

    return token_b64


def verify_download_token(
    token: str,
    secret_key: str,
    expected_client_phone: Optional[str] = None,
    expected_file_path: Optional[str] = None,
) -> DownloadTokenData:
    """Verify and decode download token.
    
    Args:
        token: Base64-encoded token string
        secret_key: HMAC secret key
        expected_client_phone: Optional client phone to verify
        expected_file_path: Optional file path to verify
        
    Returns:
        DownloadTokenData with decoded information
        
    Raises:
        DownloadTokenError: If token is invalid or expired
    """
    try:
        # Base64 decode
        import base64

        token_decoded = base64.urlsafe_b64decode(token.encode()).decode()

        # Split into payload and signature
        parts = token_decoded.split("|")
        if len(parts) != 5:
            raise DownloadTokenError("Invalid token format")

        client_phone, file_path, expiry_str, nonce, signature = parts

        # Reconstruct payload
        payload = f"{client_phone}|{file_path}|{expiry_str}|{nonce}"

        # Verify HMAC signature
        expected_signature = hmac.new(
            secret_key.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise DownloadTokenError("Invalid token signature")

        # Parse expiry
        expiry = datetime.fromisoformat(expiry_str)

        # Check expiry
        if datetime.utcnow() > expiry:
            raise DownloadTokenError(f"Token expired at {expiry}")

        # Verify client phone if provided
        if expected_client_phone and client_phone != expected_client_phone:
            raise DownloadTokenError(
                f"Client phone mismatch. Expected: {expected_client_phone}, "
                f"Got: {client_phone}"
            )

        # Verify file path if provided
        if expected_file_path and file_path != expected_file_path:
            raise DownloadTokenError(
                f"File path mismatch. Expected: {expected_file_path}, Got: {file_path}"
            )

        return DownloadTokenData(
            client_phone=client_phone, file_path=file_path, expiry=expiry, nonce=nonce
        )

    except DownloadTokenError:
        raise
    except Exception as e:
        raise DownloadTokenError(f"Token validation failed: {str(e)}") from e


def is_token_expired(token_data: DownloadTokenData) -> bool:
    """Check if token is expired.
    
    Args:
        token_data: Decoded token data
        
    Returns:
        True if token is expired
    """
    return datetime.utcnow() > token_data.expiry
