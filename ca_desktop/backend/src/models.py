"""Database models for CA Desktop."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    """CA admin user."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(255), nullable=True)  # For public profile
    slug = Column(String(50), unique=True, nullable=True, index=True)  # URL-safe identifier
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    messages_sent = relationship("Message", back_populates="sent_by_user")
    shared_files_sent = relationship("SharedFile", back_populates="sent_by_user")
    ca_profile = relationship("CAProfile", back_populates="ca_user", uselist=False)
    media_items = relationship("CAMediaItem", back_populates="ca_user")
    services = relationship("Service", back_populates="ca_user")
    testimonials = relationship("Testimonial", back_populates="ca_user")
    reminders = relationship("Reminder", back_populates="created_by_user")


class Client(Base):
    """Client account."""

    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    client_type = Column(String(50), nullable=True)  # 'Salaried', 'Business', 'Partnership'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    documents = relationship("Document", back_populates="client", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="client", cascade="all, delete-orphan")
    shared_files = relationship("SharedFile", back_populates="client", cascade="all, delete-orphan")
    downloads = relationship("Download", back_populates="client", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="client", cascade="all, delete-orphan")


class Session(Base):
    """Active session for CA or client."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    user_type = Column(String(10), nullable=False)  # 'ca' or 'client'
    user_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)


class Document(Base):
    """Indexed document metadata."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(
        String(15),
        ForeignKey("clients.phone_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    year = Column(String(10), nullable=False, index=True)
    document_type = Column(String(100), nullable=False)  # stem of filename
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA256
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    is_tagged = Column(Boolean, default=False, nullable=False)
    tag_confidence = Column(Float, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="documents")
    tags = relationship(
        "DocumentTag", secondary="document_document_tag", back_populates="documents"
    )

    __table_args__ = (
        Index("idx_client_year_filename", "client_phone", "year", "file_name", unique=True),
    )


class DocumentTag(Base):
    """Document tag/category."""

    __tablename__ = "document_tag"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)  # 'ITR', 'Form 16', etc.
    description = Column(String(255), nullable=True)
    regex_pattern = Column(String(255), nullable=True)  # e.g., 'ITR|Income Tax Return'
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    documents = relationship("Document", secondary="document_document_tag", back_populates="tags")


# Junction table for Document-Tag relationship
document_document_tag = Table(
    "document_document_tag",
    Base.metadata,
    Column(
        "document_id",
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "tag_id",
        Integer,
        ForeignKey("document_tag.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class ComplianceRule(Base):
    """Compliance requirement rules."""

    __tablename__ = "compliance_rule"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 'Salaried ITR', 'Business ITR', etc.
    description = Column(Text, nullable=True)
    client_type = Column(
        String(50), nullable=False, index=True
    )  # 'Salaried', 'Business', 'Partnership'
    required_document_tags = Column(
        JSON, nullable=False
    )  # List of tag names: ['ITR', 'Form 16', 'Bank Statement']
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Reminder(Base):
    """Reminders and notifications."""

    __tablename__ = "reminder"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(
        String(15),
        ForeignKey("clients.phone_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reminder_type = Column(String(50), nullable=False)  # 'document', 'custom'
    
    # Document details (instead of tag_id)
    document_name = Column(String(255), nullable=True)  # e.g., "ITR Filing", "GST Return"
    document_type = Column(String(100), nullable=True)  # e.g., "ITR", "GST_GSTR3B", "PAN_CARD"
    document_year = Column(String(10), nullable=True)  # e.g., "2025", "2025-26"
    
    # Legacy fields (kept for backward compatibility)
    tag_id = Column(
        Integer, ForeignKey("document_tag.id"), nullable=True
    )
    compliance_rule_id = Column(
        Integer, ForeignKey("compliance_rule.id"), nullable=True
    )
    
    reminder_date = Column(DateTime, nullable=False, index=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    recurrence_pattern = Column(String(50), nullable=True)  # 'yearly', 'quarterly', 'monthly'
    message = Column(Text, nullable=True)  # General instructions
    
    # Sending options
    send_via_email = Column(Boolean, default=True, nullable=False)
    send_via_whatsapp = Column(Boolean, default=False, nullable=False)
    
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime, nullable=True)
    email_sent = Column(Boolean, default=False, nullable=False)
    whatsapp_sent = Column(Boolean, default=False, nullable=False)
    
    created_by_ca_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="reminders")
    tag = relationship("DocumentTag")
    compliance_rule = relationship("ComplianceRule")
    created_by_user = relationship("User", back_populates="reminders")

    __table_args__ = (Index("idx_client_reminder_date", "client_phone", "reminder_date"),)


class CAProfile(Base):
    """CA professional profile information."""

    __tablename__ = "ca_profile"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    firm_name = Column(String(255), nullable=True)
    logo_file_path = Column(String(255), nullable=True)  # Path relative to uploads/
    professional_bio = Column(Text, nullable=True)
    address = Column(String(500), nullable=True)
    gstin_pan = Column(String(50), nullable=True)
    phone_number = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    website_url = Column(String(255), nullable=True)
    linkedin_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    ca_user = relationship("User", back_populates="ca_profile")


class CAMediaItem(Base):
    """Media items for CA (carousel photos, service images, etc.)."""

    __tablename__ = "ca_media_item"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_type = Column(
        String(50), nullable=False
    )  # 'carousel', 'service_background', 'testimonial_photo'
    file_path = Column(String(255), nullable=False)  # Path relative to uploads/
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ca_user = relationship("User", back_populates="media_items")

    __table_args__ = (Index("idx_ca_type_order", "ca_id", "item_type", "order_index"),)


class Service(Base):
    """Services offered by CA."""

    __tablename__ = "service"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    background_image_path = Column(String(255), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ca_user = relationship("User", back_populates="services")


class Testimonial(Base):
    """Client testimonials."""

    __tablename__ = "testimonial"

    id = Column(Integer, primary_key=True, index=True)
    ca_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    client_name = Column(String(255), nullable=False)
    text = Column(String(1000), nullable=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    verified_client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    ca_user = relationship("User", back_populates="testimonials")


class Message(Base):
    """Message from CA to client."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(
        String(15),
        ForeignKey("clients.phone_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    sent_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="messages")
    sent_by_user = relationship("User", back_populates="messages_sent")


class SharedFile(Base):
    """Manually shared file from CA to client."""

    __tablename__ = "shared_files"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(
        String(15),
        ForeignKey("clients.phone_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA256
    description = Column(Text, nullable=True)
    sent_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_downloaded = Column(Boolean, default=False, nullable=False)
    downloaded_at = Column(DateTime, nullable=True)

    # Relationships
    client = relationship("Client", back_populates="shared_files")
    sent_by_user = relationship("User", back_populates="shared_files_sent")


class Download(Base):
    """Download history/audit log."""

    __tablename__ = "downloads"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(
        String(15),
        ForeignKey("clients.phone_number", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    download_type = Column(String(20), nullable=False)  # 'document' or 'shared_file'
    file_id = Column(Integer, nullable=False)  # ID from documents or shared_files
    download_token = Column(String(255), nullable=False, unique=True)  # For single-use enforcement
    downloaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, default=True, nullable=False)

    # Relationships
    client = relationship("Client", back_populates="downloads")


class AuditLog(Base):
    """Security and access audit log."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    user_type = Column(String(10), nullable=True)  # 'ca' or 'client'
    user_id = Column(String(100), nullable=True)  # User ID or client phone
    event_details = Column(Text, nullable=True)  # JSON serialized
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    severity = Column(String(20), default="INFO", nullable=False)


class TaskQueue(Base):
    """Background task queue."""

    __tablename__ = "task_queue"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False, index=True)
    task_payload = Column(Text, nullable=True)  # JSON serialized
    status = Column(String(20), default="pending", nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)


class DocumentUpload(Base):
    """Documents uploaded by clients via WhatsApp."""

    __tablename__ = "document_uploads"

    id = Column(Integer, primary_key=True, index=True)
    client_phone = Column(String(15), ForeignKey("clients.phone_number", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    mime_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)


class WhatsAppBotState(Base):
    """Bot state for WhatsApp conversations."""

    __tablename__ = "whatsapp_bot_state"

    phone_number = Column(String(15), primary_key=True)
    bot_enabled = Column(Boolean, default=True, nullable=False)
    last_interaction = Column(DateTime, nullable=True)
    current_flow = Column(String(50), nullable=True)
