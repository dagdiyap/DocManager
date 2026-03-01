"""Database models for License Server."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class CA(Base):
    """CA (Chartered Accountant) account."""

    __tablename__ = "cas"

    id = Column(String(255), primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(15), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    devices = relationship("Device", back_populates="ca", cascade="all, delete-orphan")
    licenses = relationship(
        "License", back_populates="ca", cascade="all, delete-orphan"
    )
    support_sessions = relationship(
        "SupportSession", back_populates="ca", cascade="all, delete-orphan"
    )


class Device(Base):
    """Registered device for a CA."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(
        String(255), ForeignKey("cas.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(String(64), unique=True, nullable=False, index=True)
    device_fingerprint = Column(Text, nullable=False)
    device_info = Column(JSON, nullable=True)  # Additional device metadata
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    ca = relationship("CA", back_populates="devices")


class License(Base):
    """License token for a CA."""

    __tablename__ = "licenses"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(
        String(255), ForeignKey("cas.id", ondelete="CASCADE"), nullable=False
    )
    device_id = Column(String(64), nullable=False, index=True)
    license_token = Column(Text, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    revoked_by = Column(String(255), nullable=True)  # Admin who revoked
    revocation_reason = Column(Text, nullable=True)

    # Relationships
    ca = relationship("CA", back_populates="licenses")


class SupportSession(Base):
    """Remote support session."""

    __tablename__ = "support_sessions"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(
        String(255), ForeignKey("cas.id", ondelete="CASCADE"), nullable=False
    )
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    connected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    disconnected_at = Column(DateTime, nullable=True)
    developer_id = Column(String(255), nullable=True)  # Developer who connected
    status = Column(
        String(20), default="active", nullable=False
    )  # active, expired, closed

    # Relationships
    ca = relationship("CA", back_populates="support_sessions")
    commands = relationship(
        "RemoteCommand", back_populates="session", cascade="all, delete-orphan"
    )


class RemoteCommand(Base):
    """Remote command executed during support session."""

    __tablename__ = "remote_commands"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("support_sessions.id", ondelete="CASCADE"), nullable=False
    )
    ca_id = Column(
        String(255), ForeignKey("cas.id", ondelete="CASCADE"), nullable=False
    )
    command_type = Column(
        String(100), nullable=False, index=True
    )  # diagnostics, update, fix
    command_payload = Column(JSON, nullable=True)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_by_ca = Column(Boolean, default=False, nullable=False)
    success = Column(Boolean, nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    session = relationship("SupportSession", back_populates="commands")


class AppVersion(Base):
    """CA Desktop application versions."""

    __tablename__ = "app_versions"

    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False, index=True)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)  # SHA256
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    uploaded_by = Column(String(255), nullable=True)
    release_notes = Column(Text, nullable=True)
    is_latest = Column(Boolean, default=False, nullable=False)
    download_count = Column(Integer, default=0, nullable=False)


class AuditLog(Base):
    """Audit log for security events."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    ca_id = Column(String(255), nullable=True, index=True)
    device_id = Column(String(64), nullable=True)
    event_details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(
        String(20), default="INFO", nullable=False
    )  # DEBUG, INFO, WARNING, ERROR, CRITICAL
