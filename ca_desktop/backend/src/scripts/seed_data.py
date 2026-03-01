from sqlalchemy.orm import Session

from ..models import ComplianceRule, DocumentTag


def seed_default_tags(db: Session) -> None:
    default_tags = [
        ("ITR", "Income Tax Return", r"ITR|Income Tax Return|income tax"),
        ("Form 16", "Salary Certificate", r"Form 16|Form16|F16|salary certificate"),
        ("Bank Statement", "Bank Account Statement", r"Bank|Statement|bank statement"),
        ("GST Return", "Goods & Services Tax Return", r"GST|GSTR|Return|gst return"),
        ("Notice", "Tax Notice or Order", r"Notice|Order|notice|order"),
        ("Audit Report", "Statutory Audit Certificate", r"Audit|Report|audit report"),
    ]

    count = 0
    for name, desc, pattern in default_tags:
        existing = db.query(DocumentTag).filter(DocumentTag.name == name).first()
        if not existing:
            tag = DocumentTag(name=name, description=desc, regex_pattern=pattern)
            db.add(tag)
            count += 1

    if count > 0:
        db.commit()
        print(f"Seeded {count} tags.")
    else:
        print("Tags already up to date.")


def seed_default_compliance_rules(db: Session) -> None:
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
