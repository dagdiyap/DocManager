"""Production-optimized configuration for packaged application."""

import os
import secrets
import sys
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


def get_app_dir() -> Path:
    """Get application directory for packaged app."""
    if getattr(sys, 'frozen', False):
        # Running as packaged executable
        return Path(sys.executable).parent
    else:
        # Running in development
        return Path(__file__).parent.parent.parent.parent


def get_data_dir() -> Path:
    """Get data directory (writable location)."""
    app_dir = get_app_dir()
    
    if getattr(sys, 'frozen', False):
        # Production: Use AppData on Windows, or app dir on others
        if sys.platform == 'win32':
            # Windows: %LOCALAPPDATA%\DocManager
            data_dir = Path(os.environ.get('LOCALAPPDATA', app_dir)) / 'DocManager'
        else:
            # Mac/Linux: Use app directory
            data_dir = app_dir / 'data'
    else:
        # Development
        data_dir = app_dir / 'data'
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class ProductionSettings(BaseSettings):
    """Production-optimized settings."""
    
    # Application Info
    app_name: str = "DocManager CA Desktop"
    app_version: str = "1.0.0"
    
    # Server Configuration (Production)
    host: str = "127.0.0.1"  # Localhost only for security
    port: int = 8443
    reload: bool = False  # No auto-reload in production
    workers: int = 1  # Single worker for desktop app
    
    # Database (Production location)
    database_url: str = f"sqlite:///{get_data_dir()}/ca_desktop.db"
    
    # Document Storage (Production location)
    documents_root: str = str(get_data_dir() / "uploads")
    
    # Frontend URL
    frontend_url: str = "http://localhost:5174"
    
    # CORS (Restrict to localhost)
    cors_origins: list[str] = [
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ]
    
    # Security — auto-generated if not set so non-technical CAs aren't blocked
    secret_key: str = os.environ.get("SECRET_KEY") or secrets.token_urlsafe(48)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Email Configuration
    resend_api_key: Optional[str] = os.environ.get("RESEND_API_KEY")
    
    # Logging (Production - Less verbose)
    log_level: str = "INFO"  # Changed from DEBUG
    log_file: str = str(get_data_dir() / "logs" / "backend.log")
    
    # Performance Optimization
    uvicorn_log_config: Optional[dict] = None  # Disable uvicorn access logs
    
    model_config = SettingsConfigDict(
        env_file=str(get_data_dir() / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


_settings_cache: Optional[ProductionSettings] = None


def get_production_settings() -> ProductionSettings:
    """Get cached production settings."""
    global _settings_cache
    if _settings_cache is None:
        _settings_cache = ProductionSettings()
        
        # Ensure directories exist
        Path(_settings_cache.documents_root).mkdir(parents=True, exist_ok=True)
        Path(_settings_cache.log_file).parent.mkdir(parents=True, exist_ok=True)
    
    return _settings_cache
