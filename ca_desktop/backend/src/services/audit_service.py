"""Audit logging service for tracking critical actions."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session
from shared.utils.logging import get_logger

from ca_desktop.backend.src.models import AuditLog

logger = get_logger(__name__)


def log_audit_event(
    db: Session,
    event_type: str,
    user_type: Optional[str] = None,
    user_id: Optional[str] = None,
    event_details: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """
    Log an audit event to the database.
    
    Args:
        db: Database session
        event_type: Type of event (e.g., 'client_created', 'document_uploaded')
        user_type: Type of user ('ca' or 'client')
        user_id: User ID (phone number for clients, username for CA)
        event_details: JSON string with additional details
        ip_address: IP address of the request
    """
    try:
        audit_log = AuditLog(
            event_type=event_type,
            user_type=user_type,
            user_id=user_id,
            event_details=event_details,
            ip_address=ip_address,
            created_at=datetime.now(timezone.utc),
        )
        db.add(audit_log)
        db.commit()
        logger.info(f"Audit log created: {event_type} by {user_type}:{user_id}")
    except Exception as e:
        logger.error(f"Failed to create audit log: {e}")
        db.rollback()


# Convenience functions for common audit events

def log_client_created(db: Session, ca_username: str, client_phone: str, ip_address: Optional[str] = None) -> None:
    """Log client creation event."""
    log_audit_event(
        db=db,
        event_type="client_created",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"client_phone": "{client_phone}"}}',
        ip_address=ip_address,
    )


def log_client_updated(db: Session, ca_username: str, client_phone: str, ip_address: Optional[str] = None) -> None:
    """Log client update event."""
    log_audit_event(
        db=db,
        event_type="client_updated",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"client_phone": "{client_phone}"}}',
        ip_address=ip_address,
    )


def log_client_deleted(db: Session, ca_username: str, client_phone: str, ip_address: Optional[str] = None) -> None:
    """Log client deletion event."""
    log_audit_event(
        db=db,
        event_type="client_deleted",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"client_phone": "{client_phone}"}}',
        ip_address=ip_address,
    )


def log_document_uploaded(
    db: Session,
    user_type: str,
    user_id: str,
    client_phone: str,
    file_name: str,
    ip_address: Optional[str] = None,
) -> None:
    """Log document upload event."""
    log_audit_event(
        db=db,
        event_type="document_uploaded",
        user_type=user_type,
        user_id=user_id,
        event_details=f'{{"client_phone": "{client_phone}", "file_name": "{file_name}"}}',
        ip_address=ip_address,
    )


def log_document_downloaded(
    db: Session,
    user_type: str,
    user_id: str,
    document_id: int,
    ip_address: Optional[str] = None,
) -> None:
    """Log document download event."""
    log_audit_event(
        db=db,
        event_type="document_downloaded",
        user_type=user_type,
        user_id=user_id,
        event_details=f'{{"document_id": {document_id}}}',
        ip_address=ip_address,
    )


def log_document_deleted(
    db: Session,
    ca_username: str,
    document_id: int,
    ip_address: Optional[str] = None,
) -> None:
    """Log document deletion event."""
    log_audit_event(
        db=db,
        event_type="document_deleted",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"document_id": {document_id}}}',
        ip_address=ip_address,
    )


def log_login_attempt(
    db: Session,
    user_type: str,
    user_id: str,
    success: bool,
    ip_address: Optional[str] = None,
) -> None:
    """Log login attempt (success or failure)."""
    event_type = "login_success" if success else "login_failed"
    log_audit_event(
        db=db,
        event_type=event_type,
        user_type=user_type,
        user_id=user_id,
        event_details=None,
        ip_address=ip_address,
    )


def log_password_changed(
    db: Session,
    user_type: str,
    user_id: str,
    ip_address: Optional[str] = None,
) -> None:
    """Log password change event."""
    log_audit_event(
        db=db,
        event_type="password_changed",
        user_type=user_type,
        user_id=user_id,
        event_details=None,
        ip_address=ip_address,
    )


def log_reminder_created(
    db: Session,
    ca_username: str,
    reminder_id: int,
    client_phone: str,
    ip_address: Optional[str] = None,
) -> None:
    """Log reminder creation event."""
    log_audit_event(
        db=db,
        event_type="reminder_created",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"reminder_id": {reminder_id}, "client_phone": "{client_phone}"}}',
        ip_address=ip_address,
    )


def log_reminder_deleted(
    db: Session,
    ca_username: str,
    reminder_id: int,
    ip_address: Optional[str] = None,
) -> None:
    """Log reminder deletion event."""
    log_audit_event(
        db=db,
        event_type="reminder_deleted",
        user_type="ca",
        user_id=ca_username,
        event_details=f'{{"reminder_id": {reminder_id}}}',
        ip_address=ip_address,
    )


def log_ca_profile_updated(
    db: Session,
    ca_username: str,
    ip_address: Optional[str] = None,
) -> None:
    """Log CA profile update event."""
    log_audit_event(
        db=db,
        event_type="ca_profile_updated",
        user_type="ca",
        user_id=ca_username,
        event_details=None,
        ip_address=ip_address,
    )
