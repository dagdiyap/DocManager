"""Input validation utilities."""

import re
from pathlib import Path
from typing import Optional


class ValidationError(Exception):
    """Base validation error."""

    pass


class PhoneNumberError(ValidationError):
    """Phone number validation error."""

    pass


def validate_phone_number(phone: str) -> str:
    """Validate and normalize phone number.

    Args:
        phone: Phone number string

    Returns:
        Normalized phone number (digits only)

    Raises:
        PhoneNumberError: If phone number is invalid
    """
    # Remove all non-digit characters
    digits = re.sub(r"\D", "", phone)

    # Must be 10-15 digits
    if len(digits) < 10 or len(digits) > 15:
        raise PhoneNumberError(f"Phone number must be 10-15 digits, got {len(digits)} digits")

    # Must start with valid country code or digit
    if not digits[0].isdigit():
        raise PhoneNumberError("Phone number must start with a digit")

    return digits


def validate_year(year: str) -> str:
    """Validate year format.

    Args:
        year: Year string (e.g., '2024')

    Returns:
        Validated year string

    Raises:
        ValidationError: If year is invalid
    """
    # Must be 4 digits
    if not re.match(r"^\d{4}$", year):
        raise ValidationError(f"Year must be 4 digits, got: {year}")

    # Must be reasonable year (1900-2100)
    year_int = int(year)
    if year_int < 1900 or year_int > 2100:
        raise ValidationError(f"Year must be between 1900 and 2100, got: {year}")

    return year


def validate_document_type(doc_type: str) -> str:
    """Validate document type.

    Args:
        doc_type: Document type string

    Returns:
        Validated document type

    Raises:
        ValidationError: If document type is invalid
    """
    # Must be alphanumeric with underscores, no spaces
    if not re.match(r"^[a-zA-Z0-9_]+$", doc_type):
        raise ValidationError(
            f"Document type must be alphanumeric with underscores, got: {doc_type}"
        )

    # Max 50 characters
    if len(doc_type) > 50:
        raise ValidationError(f"Document type too long (max 50 chars): {doc_type}")

    return doc_type


def validate_file_path(file_path: str, allowed_extensions: Optional[list] = None) -> Path:
    """Validate file path and check for path traversal.

    Args:
        file_path: File path string
        allowed_extensions: Optional list of allowed file extensions (e.g., ['.pdf', '.jpg'])

    Returns:
        Validated Path object

    Raises:
        ValidationError: If path is invalid or contains traversal attempts
    """
    path = Path(file_path)

    # Check for path traversal attempts
    if ".." in path.parts:
        raise ValidationError(f"Path traversal detected in: {file_path}")

    # Check if path is absolute when it shouldn't be
    if path.is_absolute():
        raise ValidationError(f"Absolute paths not allowed: {file_path}")

    # Check file extension if provided
    if allowed_extensions:
        if path.suffix.lower() not in [ext.lower() for ext in allowed_extensions]:
            raise ValidationError(
                f"File extension {path.suffix} not allowed. "
                f"Allowed: {', '.join(allowed_extensions)}"
            )

    return path


_WINDOWS_RESERVED_NAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
})


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing/replacing dangerous characters.

    Handles both Windows and macOS/Linux constraints:
    - Removes characters invalid on Windows (\\/:*?"<>|)
    - Rejects Windows reserved names (CON, PRN, NUL, etc.)
    - Strips leading/trailing dots and spaces (Windows restriction)

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove characters invalid on Windows: \ / : * ? " < > |
    sanitized = re.sub(r'[\\/:*?"<>|]', "", filename)

    # Keep only alphanumeric, dash, underscore, dot, space
    sanitized = re.sub(r"[^\w\s\-.]", "", sanitized)

    # Replace multiple spaces with single space
    sanitized = re.sub(r"\s+", " ", sanitized)

    # Remove leading/trailing spaces and dots (Windows restriction)
    sanitized = sanitized.strip().strip(".")

    # If empty after sanitization, use default
    if not sanitized:
        sanitized = "file"

    # Check for Windows reserved names (e.g. CON, CON.txt)
    stem = Path(sanitized).stem.upper()
    if stem in _WINDOWS_RESERVED_NAMES:
        sanitized = f"_{sanitized}"

    return sanitized


def validate_folder_structure(phone: str, year: str, doc_type: str) -> tuple:
    """Validate complete folder structure components.

    Args:
        phone: Phone number
        year: Year string
        doc_type: Document type

    Returns:
        Tuple of (validated_phone, validated_year, validated_doc_type)

    Raises:
        ValidationError: If any component is invalid
    """
    validated_phone = validate_phone_number(phone)
    validated_year = validate_year(year)
    validated_doc_type = validate_document_type(doc_type)

    return validated_phone, validated_year, validated_doc_type


def is_safe_path(base_path: Path, target_path: Path) -> bool:
    """Check if target path is within base path (no traversal).

    Args:
        base_path: Base directory path
        target_path: Target file/directory path

    Returns:
        True if target is within base, False otherwise
    """
    try:
        base_path = base_path.resolve()
        target_path = target_path.resolve()
        return target_path.is_relative_to(base_path)
    except (ValueError, OSError):
        return False
