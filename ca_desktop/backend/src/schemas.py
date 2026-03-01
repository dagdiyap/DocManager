"""Pydantic schemas for CA Desktop Backend."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# CA Admin Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str
    display_name: Optional[str] = None


class User(UserBase):
    id: int
    display_name: Optional[str] = None
    slug: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# Client Schemas
class ClientBase(BaseModel):
    phone_number: str = Field(..., description="Primary client identifier")
    name: str
    email: Optional[EmailStr] = None
    client_type: Optional[str] = None  # Salaried, Business, Partnership, etc.


class ClientCreate(ClientBase):
    password: Optional[str] = None  # Optional - auto-generated if not provided


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    client_type: Optional[str] = None


class Client(ClientBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True


class InviteData(BaseModel):
    """Client invite card data."""
    portal_url: str
    username: str
    password: str
    qr_code_base64: str
    whatsapp_share_url: str


class ClientWithInvite(BaseModel):
    """Client creation response with invite data."""
    client: Client
    invite: InviteData


# Document Schemas
class DocumentBase(BaseModel):
    client_phone: str
    year: str
    document_type: str


class Document(DocumentBase):
    id: int
    file_name: str
    file_size: Optional[int] = None
    uploaded_at: datetime
    is_deleted: bool

    class Config:
        from_attributes = True


# Messaging Schemas
class MessageBase(BaseModel):
    client_phone: str
    subject: str
    body: str


class MessageCreate(MessageBase):
    pass


class Message(MessageBase):
    id: int
    sent_by_user_id: int
    sent_at: datetime
    is_read: bool
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Shared File Schemas
class SharedFileBase(BaseModel):
    client_phone: str
    file_name: str
    description: Optional[str] = None


class SharedFile(SharedFileBase):
    id: int
    file_size: Optional[int] = None
    sent_at: datetime
    is_downloaded: bool

    class Config:
        from_attributes = True


# Auth Schemas
class LoginRequest(BaseModel):
    username: str  # Phone for clients, username for CA
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str  # 'ca' or 'client'


# Dashboard Stats
class DashboardStats(BaseModel):
    total_clients: int
    total_documents: int
    recent_downloads: int


class AuditLog(BaseModel):
    id: int
    event_type: str
    user_type: Optional[str] = None
    user_id: Optional[str] = None
    event_details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    severity: str

    class Config:
        from_attributes = True


# ============ Phase 2 Schemas ============


# Document Tag Schemas
class DocumentTagSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    regex_pattern: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentWithTagsSchema(BaseModel):
    id: int
    client_phone: str
    year: str
    document_type: str
    file_name: str
    file_size: Optional[int] = None
    uploaded_at: datetime
    is_tagged: bool
    tag_confidence: Optional[float] = None
    tags: list[DocumentTagSchema] = []

    class Config:
        from_attributes = True


# Compliance Rule Schemas
class ComplianceRuleSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    client_type: str
    required_document_tags: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Reminder Schemas
class ReminderSchema(BaseModel):
    id: int
    client_phone: str
    reminder_type: str
    tag_id: Optional[int] = None
    compliance_rule_id: Optional[int] = None
    reminder_date: datetime
    is_recurring: bool
    recurrence_pattern: Optional[str] = None
    message: Optional[str] = None
    is_sent: bool
    sent_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


# CA Profile Schemas
class CAProfileSchema(BaseModel):
    id: int
    ca_id: int
    firm_name: Optional[str] = None
    logo_file_path: Optional[str] = None
    professional_bio: Optional[str] = None
    address: Optional[str] = None
    gstin_pan: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CAProfileUpdate(BaseModel):
    firm_name: Optional[str] = None
    professional_bio: Optional[str] = None
    address: Optional[str] = None
    gstin_pan: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    website_url: Optional[str] = None
    linkedin_url: Optional[str] = None


# CA Media Item Schemas
class CAMediaItemSchema(BaseModel):
    id: int
    ca_id: int
    item_type: str
    file_path: str
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Service Schemas
class ServiceSchema(BaseModel):
    id: int
    ca_id: int
    name: str
    description: Optional[str] = None
    background_image_path: Optional[str] = None
    order_index: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Testimonial Schemas
class TestimonialSchema(BaseModel):
    id: int
    ca_id: int
    client_name: str
    text: str
    rating: Optional[int] = None
    verified_client_id: Optional[int] = None
    order_index: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
