"""Shared package for CA Document Manager."""

from .crypto import (
    RSAKeyManager,
    generate_device_fingerprint,
    create_license_token,
    verify_license_token,
    create_download_token,
    verify_download_token,
)
from .utils import (
    validate_phone_number,
    validate_year,
    validate_document_type,
    validate_file_path,
    VALID_DOCUMENT_TYPES,
    TOKEN_EXPIRY_SECONDS,
)

__version__ = "0.1.0"

__all__ = [
    "RSAKeyManager",
    "generate_device_fingerprint",
    "create_license_token",
    "verify_license_token",
    "create_download_token",
    "verify_download_token",
    "validate_phone_number",
    "validate_year",
    "validate_document_type",
    "validate_file_path",
    "VALID_DOCUMENT_TYPES",
    "TOKEN_EXPIRY_SECONDS",
]
