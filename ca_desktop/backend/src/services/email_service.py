"""Email service using Resend API for client welcome emails."""

from typing import Optional

import resend
from shared.utils.logging import get_logger

from ca_desktop.backend.src.config import get_settings

logger = get_logger(__name__)


def send_welcome_email(
    client_email: str,
    client_name: str,
    portal_url: str,
    username: str,
    password: str,
    ca_name: str,
) -> bool:
    """
    Send welcome email to client with portal access credentials.
    
    Args:
        client_email: Client's email address
        client_name: Client's full name
        portal_url: Portal URL (e.g., https://example.com/ca-lokesh/home)
        username: Client username (phone number)
        password: Client password (plain text, sent once only)
        ca_name: CA's display name or firm name
        
    Returns:
        True if email sent successfully, False otherwise
    """
    settings = get_settings()
    
    if not settings.resend_api_key:
        logger.warning("Resend API key not configured, skipping email send")
        return False
    
    resend.api_key = settings.resend_api_key
    
    # HTML email template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background: #f9fafb;
                padding: 30px;
                border-radius: 0 0 8px 8px;
            }}
            .credentials-box {{
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .credential-item {{
                margin: 15px 0;
                padding: 10px;
                background: #f3f4f6;
                border-radius: 4px;
            }}
            .credential-label {{
                font-weight: 600;
                color: #6b7280;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            .credential-value {{
                font-size: 16px;
                color: #111827;
                margin-top: 5px;
                font-family: 'Courier New', monospace;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 14px 28px;
                text-decoration: none;
                border-radius: 6px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                color: #6b7280;
                font-size: 14px;
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #e5e7eb;
            }}
            .warning {{
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
                border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1 style="margin: 0; font-size: 28px;">Welcome to {ca_name}</h1>
            <p style="margin: 10px 0 0 0; opacity: 0.9;">Your Client Portal is Ready</p>
        </div>
        
        <div class="content">
            <p>Dear {client_name},</p>
            
            <p>Your account has been created successfully. You can now access your documents, messages, and compliance information through our secure client portal.</p>
            
            <div class="credentials-box">
                <h3 style="margin-top: 0; color: #111827;">Your Login Credentials</h3>
                
                <div class="credential-item">
                    <div class="credential-label">Portal URL</div>
                    <div class="credential-value">{portal_url}</div>
                </div>
                
                <div class="credential-item">
                    <div class="credential-label">Username</div>
                    <div class="credential-value">{username}</div>
                </div>
                
                <div class="credential-item">
                    <div class="credential-label">Password</div>
                    <div class="credential-value">{password}</div>
                </div>
            </div>
            
            <div class="warning">
                <strong>⚠️ Important:</strong> Please save these credentials securely. We recommend changing your password after your first login.
            </div>
            
            <center>
                <a href="{portal_url}" class="button">Access Your Portal</a>
            </center>
            
            <p style="margin-top: 30px;">If you have any questions or need assistance, please don't hesitate to contact us.</p>
            
            <p>Best regards,<br><strong>{ca_name}</strong></p>
        </div>
        
        <div class="footer">
            <p>This is an automated message. Please do not reply to this email.</p>
            <p>© {ca_name}. All rights reserved.</p>
        </div>
    </body>
    </html>
    """
    
    # Plain text fallback
    text_content = f"""
Welcome to {ca_name}

Dear {client_name},

Your account has been created successfully. You can now access your documents, messages, and compliance information through our secure client portal.

Your Login Credentials:
-----------------------
Portal URL: {portal_url}
Username: {username}
Password: {password}

IMPORTANT: Please save these credentials securely. We recommend changing your password after your first login.

Access your portal: {portal_url}

If you have any questions or need assistance, please don't hesitate to contact us.

Best regards,
{ca_name}

---
This is an automated message. Please do not reply to this email.
© {ca_name}. All rights reserved.
    """
    
    try:
        params = {
            "from": f"{ca_name} <onboarding@resend.dev>",  # Use verified domain in production
            "to": [client_email],
            "subject": f"Welcome to {ca_name} - Your Portal Access",
            "html": html_content,
            "text": text_content,
        }
        
        email = resend.Emails.send(params)
        logger.info(f"Welcome email sent to {client_email}, email_id: {email.get('id')}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {client_email}: {e}")
        return False
