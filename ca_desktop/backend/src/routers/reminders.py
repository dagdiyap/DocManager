"""Reminders and notifications router."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user_data
from ..models import Client, ComplianceRule, Document, DocumentTag, Reminder, User

router = APIRouter(tags=["reminders"])


@router.post("/reminders")
def create_reminder(
    client_phone: str,
    reminder_type: str,  # 'document_type', 'compliance', 'custom'
    reminder_date: datetime,
    message: Optional[str] = None,
    tag_id: Optional[int] = None,
    compliance_rule_id: Optional[int] = None,
    is_recurring: bool = False,
    recurrence_pattern: Optional[str] = None,  # 'yearly', 'quarterly', 'monthly'
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Create a new reminder."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can create reminders")

    # Verify client exists
    client = db.query(Client).filter(Client.phone_number == client_phone).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate reminder type
    if reminder_type not in ["document_type", "compliance", "custom"]:
        raise HTTPException(status_code=400, detail="Invalid reminder type")

    # Validate required fields for each type
    if reminder_type == "document_type" and not tag_id:
        raise HTTPException(status_code=400, detail="tag_id required for document_type reminders")

    if reminder_type == "compliance" and not compliance_rule_id:
        raise HTTPException(
            status_code=400,
            detail="compliance_rule_id required for compliance reminders",
        )

    # Validate tag and compliance rule exist
    if tag_id:
        tag = db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

    if compliance_rule_id:
        rule = db.query(ComplianceRule).filter(ComplianceRule.id == compliance_rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Compliance rule not found")

    # Create reminder
    reminder = Reminder(
        client_phone=client_phone,
        reminder_type=reminder_type,
        tag_id=tag_id,
        compliance_rule_id=compliance_rule_id,
        reminder_date=reminder_date,
        is_recurring=is_recurring,
        recurrence_pattern=recurrence_pattern,
        message=message,
        created_by_ca_id=current_user.get("user_id"),
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return {
        "id": reminder.id,
        "client_phone": reminder.client_phone,
        "reminder_type": reminder.reminder_type,
        "reminder_date": reminder.reminder_date.isoformat(),
        "message": reminder.message,
        "is_recurring": reminder.is_recurring,
        "recurrence_pattern": reminder.recurrence_pattern,
        "is_sent": reminder.is_sent,
    }


@router.get("/reminders")
def list_reminders(
    client_phone: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """List reminders."""
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

    reminders = query.order_by(Reminder.reminder_date).all()

    return [
        {
            "id": r.id,
            "client_phone": r.client_phone,
            "reminder_type": r.reminder_type,
            "tag": r.tag.name if r.tag else None,
            "compliance_rule": r.compliance_rule.name if r.compliance_rule else None,
            "reminder_date": r.reminder_date.isoformat(),
            "message": r.message,
            "is_sent": r.is_sent,
            "sent_at": r.sent_at.isoformat() if r.sent_at else None,
        }
        for r in reminders
    ]


@router.patch("/reminders/{reminder_id}")
def update_reminder(
    reminder_id: int,
    reminder_date: Optional[datetime] = None,
    message: Optional[str] = None,
    is_recurring: Optional[bool] = None,
    recurrence_pattern: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Update a reminder (CA only)."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can update reminders")

    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    if reminder_date:
        reminder.reminder_date = reminder_date
    if message is not None:
        reminder.message = message
    if is_recurring is not None:
        reminder.is_recurring = is_recurring
    if recurrence_pattern:
        reminder.recurrence_pattern = recurrence_pattern

    db.commit()
    db.refresh(reminder)

    return {
        "id": reminder.id,
        "client_phone": reminder.client_phone,
        "reminder_type": reminder.reminder_type,
        "reminder_date": reminder.reminder_date.isoformat(),
        "message": reminder.message,
        "is_sent": reminder.is_sent,
    }


@router.delete("/reminders/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Delete a reminder (CA only)."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can delete reminders")

    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    db.delete(reminder)
    db.commit()

    return {"status": "success", "message": "Reminder deleted"}


@router.post("/reminders/send-group")
def send_group_reminders(
    filter_type: str,  # 'missing_documents', 'upcoming_deadline', 'compliance_rule'
    tag_id: Optional[int] = None,
    compliance_rule_id: Optional[int] = None,
    message: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Send group reminders to multiple clients (CA only)."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can send group reminders")

    # Get CA user
    ca_user = db.query(User).filter(User.id == current_user.get("user_id")).first()
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA user not found")

    reminders_created = []
    affected_clients = []

    if filter_type == "missing_documents":
        # Find clients missing a specific document
        if not tag_id:
            raise HTTPException(
                status_code=400, detail="tag_id required for missing_documents filter"
            )

        tag = db.query(DocumentTag).filter(DocumentTag.id == tag_id).first()
        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        # Get all clients
        all_clients = db.query(Client).all()

        for client in all_clients:
            # Check if client has this document
            has_doc = (
                db.query(Document)
                .filter(
                    Document.client_phone == client.phone_number,
                    Document.tags.any(id=tag.id),
                    Document.is_deleted == False,  # noqa: E712
                )
                .first()
            )

            if not has_doc:
                # Create reminder
                reminder = Reminder(
                    client_phone=client.phone_number,
                    reminder_type="document_type",
                    tag_id=tag_id,
                    reminder_date=datetime.utcnow(),
                    message=message or f"Please arrange {tag.name} documents",
                    created_by_ca_id=ca_user.id,
                    is_sent=True,
                    sent_at=datetime.utcnow(),
                )
                db.add(reminder)
                reminders_created.append(reminder)
                affected_clients.append(client.phone_number)

    elif filter_type == "compliance_rule":
        # Find clients not meeting a compliance rule
        if not compliance_rule_id:
            raise HTTPException(
                status_code=400,
                detail="compliance_rule_id required for compliance_rule filter",
            )

        rule = db.query(ComplianceRule).filter(ComplianceRule.id == compliance_rule_id).first()
        if not rule:
            raise HTTPException(status_code=404, detail="Compliance rule not found")

        # Get all clients of matching type
        matching_clients = db.query(Client).filter(Client.client_type == rule.client_type).all()

        for client in matching_clients:
            # Check compliance
            missing_any = False
            for tag_name in rule.required_document_tags:
                tag = db.query(DocumentTag).filter(DocumentTag.name == tag_name).first()
                if tag:
                    has_doc = (
                        db.query(Document)
                        .filter(
                            Document.client_phone == client.phone_number,
                            Document.tags.any(id=tag.id),
                            Document.is_deleted == False,  # noqa: E712
                        )
                        .first()
                    )
                    if not has_doc:
                        missing_any = True
                        break

            if missing_any:
                reminder = Reminder(
                    client_phone=client.phone_number,
                    reminder_type="compliance",
                    compliance_rule_id=compliance_rule_id,
                    reminder_date=datetime.utcnow(),
                    message=message or f"Please arrange documents as per {rule.name}",
                    created_by_ca_id=ca_user.id,
                    is_sent=True,
                    sent_at=datetime.utcnow(),
                )
                db.add(reminder)
                reminders_created.append(reminder)
                affected_clients.append(client.phone_number)

    db.commit()

    return {
        "sent_count": len(reminders_created),
        "affected_clients": affected_clients,
        "message": f"Sent reminders to {len(affected_clients)} clients",
    }
