"""Pydantic schemas for License Server."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


# CA Schemas
class CABase(BaseModel):
    id: str = Field(..., description="Unique CA identifier")
    email: EmailStr
    name: str
    phone: str | None = None


class CACreate(CABase):
    pass


class CAUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    phone: str | None = None
    is_active: bool | None = None


class CA(CABase):
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# Device Schemas
class DeviceBase(BaseModel):
    device_id: str
    device_fingerprint: str
    device_info: dict[str, Any] | None = None


class DeviceCreate(DeviceBase):
    ca_id: str


class Device(DeviceBase):
    id: int
    ca_id: str
    registered_at: datetime
    last_seen: datetime | None = None

    class Config:
        from_attributes = True


# License Schemas
class LicenseBase(BaseModel):
    ca_id: str
    device_id: str
    expires_at: datetime


class LicenseCreate(LicenseBase):
    expiry_days: int | None = Field(
        None, description="Expiration in days (overrides expires_at if provided)"
    )


class License(LicenseBase):
    id: int
    license_token: str
    issued_at: datetime
    is_active: bool
    revoked_at: datetime | None = None
    revocation_reason: str | None = None

    class Config:
        from_attributes = True


# Support & Monitoring Schemas
class SupportSessionBase(BaseModel):
    ca_id: str
    developer_id: str | None = None


class SupportSessionCreate(SupportSessionBase):
    pass


class SupportSession(SupportSessionBase):
    id: int
    session_token: str
    connected_at: datetime
    disconnected_at: datetime | None = None
    status: str

    class Config:
        from_attributes = True


class RemoteCommandBase(BaseModel):
    session_id: int
    ca_id: str
    command_type: str
    command_payload: dict[str, Any] | None = None


class RemoteCommandCreate(RemoteCommandBase):
    pass


class RemoteCommand(RemoteCommandBase):
    id: int
    executed_at: datetime
    approved_by_ca: bool
    success: bool | None = None
    result: dict[str, Any] | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True


# App Version Schemas
class AppVersionBase(BaseModel):
    version: str
    release_notes: str | None = None
    is_latest: bool = False


class AppVersionCreate(AppVersionBase):
    file_path: str
    file_hash: str


class AppVersion(AppVersionBase):
    id: int
    file_path: str
    file_hash: str
    uploaded_at: datetime
    download_count: int

    class Config:
        from_attributes = True


# Auth & Common
class Token(BaseModel):
    access_token: str
    token_type: str


class StatusResponse(BaseModel):
    status: str
    version: str
    db_connected: bool
    timestamp: datetime
