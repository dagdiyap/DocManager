"""Compliance calendar router."""

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user_data
from ..models import Client, ComplianceRule, Document, DocumentTag
from ..schemas import ComplianceRuleSchema

router = APIRouter(tags=["compliance"])


@router.get("/compliance/rules", response_model=list[ComplianceRuleSchema])
def list_compliance_rules(
    client_type: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list[ComplianceRule]:
    """List all compliance rules, optionally filtered by client type."""
    query = db.query(ComplianceRule)

    if client_type:
        query = query.filter(ComplianceRule.client_type == client_type)

    rules = query.all()
    return rules


@router.get("/clients/{client_phone}/compliance")
def get_client_compliance_status(
    client_phone: str,
    year: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
) -> dict[str, Any]:
    """Get compliance status for a client."""
    # Verify access
    if current_user.get("user_type") == "client":
        if client_phone != current_user.get("phone_number"):
            raise HTTPException(status_code=403, detail="Unauthorized")

    # Get client
    client = db.query(Client).filter(Client.phone_number == client_phone).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # If no client_type set, return empty compliance
    if not client.client_type:
        return {
            "client_phone": client_phone,
            "client_type": None,
            "applicable_rules": [],
            "missing_documents": [],
            "is_compliant": False,
            "message": "Client type not set",
        }

    # Get applicable rules
    rules = db.query(ComplianceRule).filter(ComplianceRule.client_type == client.client_type).all()

    # Build compliance status
    applicable_rules = []
    all_missing = []

    for rule in rules:
        required_tags = rule.required_document_tags

        rule_details = {
            "rule_id": rule.id,
            "rule_name": rule.name,
            "required_documents": [],
        }

        for tag_name in required_tags:
            # Find tag
            tag = db.query(DocumentTag).filter(DocumentTag.name == tag_name).first()

            # Check if client has document with this tag
            has_doc = False
            latest_upload = None

            if tag:
                doc_with_tag = (
                    db.query(Document)
                    .filter(
                        Document.client_phone == client_phone,
                        Document.tags.any(id=tag.id),
                        Document.is_deleted.is_(False),
                    )
                    .first()
                )

                if doc_with_tag:
                    has_doc = True
                    latest_upload = doc_with_tag.uploaded_at

            doc_status = {
                "tag_name": tag_name,
                "has_document": has_doc,
            }

            if latest_upload:
                doc_status["latest_upload_date"] = latest_upload.isoformat()

            rule_details["required_documents"].append(doc_status)

            if not has_doc:
                all_missing.append({"tag": tag_name, "rule": rule.name})

        applicable_rules.append(rule_details)

    is_compliant = len(all_missing) == 0

    return {
        "client_phone": client_phone,
        "client_type": client.client_type,
        "applicable_rules": applicable_rules,
        "missing_documents": all_missing,
        "is_compliant": is_compliant,
        "total_required": sum(len(r["required_documents"]) for r in applicable_rules),
        "missing_count": len(all_missing),
    }
