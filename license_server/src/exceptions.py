"""Custom exceptions for License Server."""

from typing import Any


class LicenseServerError(Exception):
    """Base exception for License Server."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
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


class ConfigurationError(LicenseServerError):
    """Configuration error."""

    pass


class DatabaseError(LicenseServerError):
    """Database operation error."""

    pass


class CANotFoundError(LicenseServerError):
    """CA not found."""

    pass


class CAAlreadyExistsError(LicenseServerError):
    """CA already exists."""

    pass


class DeviceFingerprintMismatchError(LicenseServerError):
    """Device fingerprint mismatch."""

    pass


class LicenseGenerationError(LicenseServerError):
    """License token generation error."""

    pass


class LicenseValidationError(LicenseServerError):
    """License validation error."""

    pass


class LicenseExpiredError(LicenseServerError):
    """License has expired."""

    pass


class LicenseRevokedError(LicenseServerError):
    """License has been revoked."""

    pass


class InvalidCredentialsError(LicenseServerError):
    """Invalid login credentials."""

    pass


class UnauthorizedError(LicenseServerError):
    """Unauthorized access."""

    pass


class RateLimitExceededError(LicenseServerError):
    """Rate limit exceeded."""

    pass


class WebSocketError(LicenseServerError):
    """WebSocket connection error."""

    pass


class RemoteSupportError(LicenseServerError):
    """Remote support operation error."""

    pass


class UpdatePushError(LicenseServerError):
    """Error pushing update to CA desktop."""

    pass
