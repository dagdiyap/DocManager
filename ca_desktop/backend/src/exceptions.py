"""Custom exceptions for CA Desktop Backend."""

from typing import Any, Optional


class CADesktopError(Exception):
    """Base exception for CA Desktop."""

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize exception.

        Args:
            message: Error message
            error_code: Optional error code
            details: Optional additional details
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}


class ConfigurationError(CADesktopError):
    """Configuration error."""

    pass


class DatabaseError(CADesktopError):
    """Database operation error."""

    pass


class ClientNotFoundError(CADesktopError):
    """Client not found."""

    pass


class ClientAlreadyExistsError(CADesktopError):
    """Client already exists."""

    pass


class DocumentNotFoundError(CADesktopError):
    """Document not found."""

    pass


class DocumentScanError(CADesktopError):
    """Error scanning documents."""

    pass


class InvalidFolderStructureError(CADesktopError):
    """Invalid folder structure."""

    pass


class FileAccessError(CADesktopError):
    """File access error."""

    pass


class FileNotFoundError(CADesktopError):
    """File not found."""

    pass


class FileTooLargeError(CADesktopError):
    """File size exceeds maximum allowed."""

    pass


class InvalidTokenError(CADesktopError):
    """Invalid download token."""

    pass


class TokenExpiredError(CADesktopError):
    """Download token expired."""

    pass


class PathTraversalError(CADesktopError):
    """Path traversal attempt detected."""

    pass


class InvalidCredentialsError(CADesktopError):
    """Invalid login credentials."""

    pass


class UnauthorizedError(CADesktopError):
    """Unauthorized access."""

    pass


class SessionExpiredError(CADesktopError):
    """Session has expired."""

    pass


class RateLimitExceededError(CADesktopError):
    """Rate limit exceeded."""

    pass


class MessageError(CADesktopError):
    """Message-related error."""

    pass


class SharedFileError(CADesktopError):
    """Shared file-related error."""

    pass
