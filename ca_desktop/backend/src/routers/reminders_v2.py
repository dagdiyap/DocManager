"""Improved reminders router with multi-client, multi-document support."""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_ca, get_current_user_data
from ..models import Client, Reminder, User
from ..services.reminder_service import send_bulk_reminders
from shared.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/reminders", tags=["Reminders"])


class ReminderCreate(BaseModel):
    """Schema for creating a reminder."""
    client_phones: List[str]  # Support multiple clients
    document_names: List[str]  # Support multiple documents
    document_types: List[str]  # Document types (ITR, GST, etc.)
    document_years: Optional[List[str]] = None  # Years for each document
    reminder_date: datetime
    general_instructions: Optional[str] = None
    send_via_email: bool = True
    send_via_whatsapp: bool = False
    is_recurring: bool = False
    recurrence_pattern: Optional[str] = None


class BulkReminderResponse(BaseModel):
    """Response for bulk reminder creation."""
    reminders_created: int
    emails_sent: int
    emails_failed: int
    whatsapp_urls_generated: int
    details: List[dict]


@router.post("/", response_model=BulkReminderResponse, status_code=status.HTTP_201_CREATED)
def create_reminders(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    current_ca: User = Depends(get_current_ca),
):
    """Create reminders for multiple clients and documents."""
    
    # Validate clients exist
    clients = []
    for phone in reminder_data.client_phones:
        client = db.query(Client).filter(Client.phone_number == phone).first()
        if not client:
            raise HTTPException(
                status_code=404,
                detail=f"Client with phone {phone} not found"
            )
        clients.append({
            'name': client.name,
            'email': client.email,
            'phone_number': client.phone_number,
        })
    
    # Validate document counts match
    if len(reminder_data.document_names) != len(reminder_data.document_types):
        raise HTTPException(
            status_code=400,
            detail="Number of document names must match number of document types"
        )
    
    # Prepare years list
    years = reminder_data.document_years or [None] * len(reminder_data.document_names)
    
    # Create reminders in database
    reminders_created = []
    for client_phone in reminder_data.client_phones:
        for i, doc_name in enumerate(reminder_data.document_names):
            reminder = Reminder(
                client_phone=client_phone,
                reminder_type="document",
                document_name=doc_name,
                document_type=reminder_data.document_types[i],
                document_year=years[i] if i < len(years) else None,
                reminder_date=reminder_data.reminder_date,
                message=reminder_data.general_instructions,
                send_via_email=reminder_data.send_via_email,
                send_via_whatsapp=reminder_data.send_via_whatsapp,
                is_recurring=reminder_data.is_recurring,
                recurrence_pattern=reminder_data.recurrence_pattern,
                created_by_ca_id=current_ca.id,
            )
            db.add(reminder)
            reminders_created.append(reminder)
    
    db.commit()
    
    # Send reminders via email/WhatsApp
    ca_name = current_ca.display_name or current_ca.username
    
    send_results = send_bulk_reminders(
        clients=clients,
        document_names=reminder_data.document_names,
        document_types=reminder_data.document_types,
        document_years=years,
        general_instructions=reminder_data.general_instructions,
        ca_name=ca_name,
        send_email=reminder_data.send_via_email,
        send_whatsapp=reminder_data.send_via_whatsapp,
    )
    
    # Update sent status in database
    for reminder in reminders_created:
        reminder.is_sent = True
        reminder.sent_at = datetime.now(timezone.utc)
        if reminder_data.send_via_email:
            reminder.email_sent = True
        if reminder_data.send_via_whatsapp:
            reminder.whatsapp_sent = True
    
    db.commit()
    
    return BulkReminderResponse(
        reminders_created=len(reminders_created),
        emails_sent=send_results["emails_sent"],
        emails_failed=send_results["emails_failed"],
        whatsapp_urls_generated=send_results["whatsapp_urls_generated"],
        details=send_results["details"],
    )


@router.get("/")
def list_reminders(
    client_phone: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """List reminders with optional filters."""
    
    query = db.query(Reminder)
    
    if current_user.get("user_type") == "client":
        # Clients can only see their own reminders
        query = query.filter(Reminder.client_phone == current_user.get("phone_number"))
    elif client_phone:
        # CA can filter by client
        query = query.filter(Reminder.client_phone == client_phone)
    
    if start_date:
        query = query.filter(Reminder.reminder_date >= start_date)
    
    if end_date:
        query = query.filter(Reminder.reminder_date <= end_date)
    
    reminders = query.order_by(Reminder.reminder_date.desc()).all()
    
    return [
        {
            "id": r.id,
            "client_phone": r.client_phone,
            "reminder_type": r.reminder_type,
            "document_name": r.document_name,
            "document_type": r.document_type,
            "document_year": r.document_year,
            "reminder_date": r.reminder_date.isoformat(),
            "message": r.message,
            "send_via_email": r.send_via_email,
            "send_via_whatsapp": r.send_via_whatsapp,
            "is_sent": r.is_sent,
            "email_sent": r.email_sent,
            "whatsapp_sent": r.whatsapp_sent,
            "sent_at": r.sent_at.isoformat() if r.sent_at else None,
        }
        for r in reminders
    ]


@router.delete("/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_ca: User = Depends(get_current_ca),
):
    """Delete a reminder."""
    
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    
    return {"status": "success", "message": "Reminder deleted"}


@router.get("/document-types")
def get_document_types():
    """Get list of available document types."""
    from shared.utils.constants import VALID_DOCUMENT_TYPES
    
    return {
        "document_types": VALID_DOCUMENT_TYPES,
        "common_types": [
            {"value": "ITR", "label": "Income Tax Return"},
            {"value": "GST_GSTR3B", "label": "GST Return GSTR-3B"},
            {"value": "GST_GSTR1", "label": "GST Return GSTR-1"},
            {"value": "PAN_CARD", "label": "PAN Card"},
            {"value": "AADHAR", "label": "Aadhaar Card"},
            {"value": "AUDIT_REPORT", "label": "Audit Report"},
            {"value": "BALANCE_SHEET", "label": "Balance Sheet"},
            {"value": "FORM16", "label": "Form 16"},
        ]
    }
