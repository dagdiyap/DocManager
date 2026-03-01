"""Reminder sending service for email and WhatsApp."""

import urllib.parse
from datetime import datetime
from typing import List, Optional

from shared.utils.logging import get_logger
from ..config import get_settings

logger = get_logger(__name__)


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send email using Resend API."""
    from .email_service import send_welcome_email
    
    # For now, use a simple implementation
    # In production, this should use a proper email service
    settings = get_settings()
    
    if not settings.resend_api_key:
        logger.warning("No Resend API key configured, email not sent")
        return False
    
    try:
        import resend
        resend.api_key = settings.resend_api_key
        
        params = {
            "from": "Dagdiya Associates <noreply@dagdiyaassociates.com>",
            "to": [to_email],
            "subject": subject,
            "text": body,
        }
        
        resend.Emails.send(params)
        return True
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return False


def generate_reminder_email_body(
    client_name: str,
    document_name: str,
    document_year: Optional[str],
    general_instructions: Optional[str],
    ca_name: str,
) -> str:
    """Generate reminder email body."""
    
    year_text = f" for year {document_year}" if document_year else ""
    instructions_text = f"\n\n{general_instructions}" if general_instructions else ""
    
    return f"""Dear {client_name},

This is a reminder regarding the following document:

Document Required: {document_name}{year_text}

Please arrange and submit this document at your earliest convenience.{instructions_text}

If you have already submitted this document, please ignore this reminder.

Best regards,
{ca_name}

---
This is an automated reminder from Dagdiya Associates.
"""


def generate_whatsapp_message(
    client_name: str,
    document_name: str,
    document_year: Optional[str],
    general_instructions: Optional[str],
    ca_name: str,
) -> str:
    """Generate WhatsApp message text."""
    
    year_text = f" for year {document_year}" if document_year else ""
    instructions_text = f"\n\n{general_instructions}" if general_instructions else ""
    
    return f"""Dear {client_name},

Reminder: Please arrange *{document_name}*{year_text}

{ca_name}
Dagdiya Associates{instructions_text}"""


def generate_whatsapp_url(phone_number: str, message: str) -> str:
    """Generate WhatsApp share URL."""
    
    # Remove any non-digit characters from phone
    clean_phone = ''.join(filter(str.isdigit, phone_number))
    
    # Add country code if not present (assuming India +91)
    if not clean_phone.startswith('91') and len(clean_phone) == 10:
        clean_phone = '91' + clean_phone
    
    encoded_message = urllib.parse.quote(message)
    
    return f"https://wa.me/{clean_phone}?text={encoded_message}"


def send_reminder_email(
    client_email: str,
    client_name: str,
    document_name: str,
    document_year: Optional[str],
    general_instructions: Optional[str],
    ca_name: str,
) -> bool:
    """Send reminder via email."""
    
    if not client_email:
        logger.warning(f"No email address for client {client_name}")
        return False
    
    subject = f"Reminder: {document_name} Required"
    body = generate_reminder_email_body(
        client_name=client_name,
        document_name=document_name,
        document_year=document_year,
        general_instructions=general_instructions,
        ca_name=ca_name,
    )
    
    try:
        success = send_email(
            to_email=client_email,
            subject=subject,
            body=body,
        )
        
        if success:
            logger.info(f"Reminder email sent to {client_email} for {document_name}")
        else:
            logger.warning(f"Failed to send reminder email to {client_email}")
        
        return success
    except Exception as e:
        logger.error(f"Error sending reminder email: {e}")
        return False


def send_bulk_reminders(
    clients: List[dict],
    document_names: List[str],
    document_types: List[str],
    document_years: List[Optional[str]],
    general_instructions: Optional[str],
    ca_name: str,
    send_email: bool = True,
    send_whatsapp: bool = False,
) -> dict:
    """Send reminders to multiple clients for multiple documents."""
    
    results = {
        "total_clients": len(clients),
        "total_documents": len(document_names),
        "emails_sent": 0,
        "emails_failed": 0,
        "whatsapp_urls_generated": 0,
        "details": []
    }
    
    for client in clients:
        client_name = client.get('name', 'Client')
        client_email = client.get('email')
        client_phone = client.get('phone_number')
        
        for i, doc_name in enumerate(document_names):
            doc_year = document_years[i] if i < len(document_years) else None
            
            client_result = {
                "client_name": client_name,
                "client_phone": client_phone,
                "document_name": doc_name,
                "email_sent": False,
                "whatsapp_url": None,
            }
            
            # Send email
            if send_email and client_email:
                email_success = send_reminder_email(
                    client_email=client_email,
                    client_name=client_name,
                    document_name=doc_name,
                    document_year=doc_year,
                    general_instructions=general_instructions,
                    ca_name=ca_name,
                )
                
                if email_success:
                    results["emails_sent"] += 1
                    client_result["email_sent"] = True
                else:
                    results["emails_failed"] += 1
            
            # Generate WhatsApp URL
            if send_whatsapp and client_phone:
                message = generate_whatsapp_message(
                    client_name=client_name,
                    document_name=doc_name,
                    document_year=doc_year,
                    general_instructions=general_instructions,
                    ca_name=ca_name,
                )
                
                whatsapp_url = generate_whatsapp_url(client_phone, message)
                client_result["whatsapp_url"] = whatsapp_url
                results["whatsapp_urls_generated"] += 1
            
            results["details"].append(client_result)
    
    return results
