from sqlalchemy.orm import Session

from ..models import ComplianceRule


def seed_default_compliance_rules(db: Session) -> None:
    """Seed default compliance rules if they don't exist."""
    default_rules = [
        {
            "name": "Salaried Employee Compliance",
            "client_type": "Salaried",
            "required_document_tags": ["ITR", "Form 16", "Bank Statement"],
        },
        {
            "name": "Business Owner Compliance",
            "client_type": "Business",
            "required_document_tags": ["ITR", "GST Return", "Audit Report"],
        },
        {
            "name": "Partnership Compliance",
            "client_type": "Partnership",
            "required_document_tags": ["ITR", "GST Return", "Audit Report"],
        },
    ]

    count = 0
    for rule_data in default_rules:
        existing = (
            db.query(ComplianceRule)
            .filter(ComplianceRule.client_type == rule_data["client_type"])
            .first()
        )

        if not existing:
            rule = ComplianceRule(**rule_data)
            db.add(rule)
            count += 1

    if count > 0:
        db.commit()
        print(f"Seeded {count} compliance rules.")
    else:
        print("Compliance rules already up to date.")
