"""Configuration management for License Server."""

from pathlib import Path

from pydantic import Field, PostgresDsn, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """License Server configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: PostgresDsn | str = Field(
        default="postgresql://license_admin:password@localhost:5432/license_server",
        validation_alias="LICENSE_DATABASE_URL",
        description="PostgreSQL connection string",
    )

    # Security
    secret_key: str = Field(
        min_length=32,
        validation_alias="LICENSE_JWT_SECRET",
        description="Secret key for JWT and sessions",
    )

    # RSA Keys
    private_key_path: Path = Field(
        default=Path("keys/private_key.pem"),
        description="Path to RSA private key",
    )
    public_key_path: Path = Field(
        default=Path("keys/public_key.pem"),
        description="Path to RSA public key",
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, ge=1024, le=65535, description="Server port")
    ws_port: int = Field(default=8001, ge=1024, le=65535, description="WebSocket port")
    environment: str = Field(default="development", description="Environment name")

    # License
    default_license_days: int = Field(
        default=30, ge=1, le=365, description="Default license validity in days"
    )
    max_license_days: int = Field(
        default=365, ge=1, le=365, description="Maximum license validity in days"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Path | None = Field(
        default=Path("logs/license_server.log"),
        description="Log file path",
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Rate Limiting
    rate_limit_per_minute: int = Field(
        default=60, ge=1, description="API rate limit per minute"
    )

    @validator("log_file", pre=True)
    def create_log_directory(cls, v: Path | None) -> Path | None:
        """Create log directory if it doesn't exist."""
        if v:
            v = Path(v)
            v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @validator("private_key_path", "public_key_path")
    def create_keys_directory(cls, v: Path) -> Path:
        """Create keys directory if it doesn't exist."""
        v = Path(v)
        v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @property
    def debug(self) -> bool:
        """Check if in debug mode."""
        return self.environment.lower() in ["development", "dev"]

    @property
    def database_url_str(self) -> str:
        """Get database URL as string."""
        return str(self.database_url)


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get application settings (singleton).

    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment.

    Returns:
        New Settings instance
    """
    global _settings
    _settings = Settings()
    return _settings
