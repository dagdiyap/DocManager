"""Configuration management for CA Desktop Backend."""

import os
import secrets
import sys
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _find_project_root() -> Path:
    """Find the project root directory. Works on Windows and macOS."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    current = Path(__file__).resolve().parent  # src/
    for _ in range(5):
        if (current / '.env').exists() or (current / 'ca_desktop').exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent.parent


def _find_env_file() -> Optional[str]:
    """Find .env file across platforms (Windows, macOS, Linux)."""
    candidates = [
        Path.cwd() / '.env',
        _find_project_root() / '.env',
        Path(__file__).resolve().parent.parent / '.env',
    ]
    if sys.platform == 'win32':
        appdata = os.environ.get('LOCALAPPDATA', '')
        if appdata:
            candidates.append(Path(appdata) / 'DocManager' / '.env')
    for p in candidates:
        if p.exists():
            return str(p)
    return '.env'


def _get_default_secret_key() -> str:
    """Auto-generate SECRET_KEY if not set. Non-technical CAs won't be blocked."""
    env_key = os.environ.get('SECRET_KEY') or os.environ.get('CA_SECRET_KEY')
    if env_key and len(env_key) >= 32:
        return env_key
    return secrets.token_urlsafe(48)


class Settings(BaseSettings):
    """CA Desktop Backend configuration."""

    model_config = SettingsConfigDict(
        env_file=_find_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = Field(
        default="sqlite:///../../ca_desktop.db",
        validation_alias="CA_DATABASE_URL",
        description="SQLite connection string",
    )

    # Security — auto-generated if not set, so non-technical users aren't blocked
    secret_key: str = Field(
        default_factory=_get_default_secret_key,
        validation_alias="SECRET_KEY",
        description="Secret key for JWT and HMAC",
    )

    # Public Key
    public_key_path: Path = Field(
        default=Path("keys/public_key.pem"),
        description="Path to RSA public key for license validation",
    )

    # Document Storage
    documents_root: Path = Field(
        default=Path("documents"),
        description="Root directory for client documents",
    )
    shared_files_root: Path = Field(
        default=Path("shared_files"),
        description="Root directory for manually shared files",
    )

    # Server — 127.0.0.1 for local desktop, 0.0.0.0 when EXTERNAL_ACCESS=true
    host: str = Field(
        default_factory=lambda: "0.0.0.0" if os.environ.get("EXTERNAL_ACCESS", "").lower() in ("true", "1", "yes") else "127.0.0.1",
        description="Server host",
    )
    port: int = Field(default=8443, ge=1024, le=65535, description="Server port")
    enable_https: bool = Field(default=True, description="Enable HTTPS")

    # Environment
    environment: str = Field(default="development", description="Environment name")

    # File Download
    token_expiry_seconds: int = Field(
        default=600, ge=60, le=3600, description="Download token expiry in seconds"
    )
    max_file_size_mb: int = Field(default=100, ge=1, le=1000, description="Max file size in MB")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(
        default=Path("logs/ca_desktop.log"),
        description="Log file path",
    )

    # Device Fingerprint
    device_id_file: Path = Field(
        default=Path(".device_id"),
        description="File to store device fingerprint",
    )

    # CORS — include all ports the frontend may use + external origins
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ] + [
            o.strip() for o in os.environ.get("EXTRA_CORS_ORIGINS", "").split(",") if o.strip()
        ],
        description="Allowed CORS origins",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(default=60, ge=1, description="API rate limit per minute")

    # Email Service (Resend)
    resend_api_key: Optional[str] = Field(
        default=None,
        validation_alias="RESEND_API_KEY",
        description="Resend API key for sending emails (optional)",
    )

    @validator("log_file", pre=True)
    def create_log_directory(cls, v: Optional[Path]) -> Optional[Path]:
        """Create log directory if it doesn't exist."""
        if v:
            v = Path(v)
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @validator("documents_root", "shared_files_root")
    def create_storage_directory(cls, v: Path) -> Path:
        """Create storage directory if it doesn't exist."""
        v = Path(v)
        v.mkdir(parents=True, exist_ok=True)
        return v

    @validator("public_key_path")
    def validate_public_key(cls, v: Path) -> Path:
        """Validate public key exists."""
        v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def debug(self) -> bool:
        """Check if in debug mode."""
        return self.environment.lower() in ["development", "dev"]

    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get application settings (singleton).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()  # type: ignore[call-arg]
    return _settings
