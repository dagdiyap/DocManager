"""Client invite utilities - password generation, QR codes, WhatsApp sharing."""

import base64
import io
import secrets
import string
from urllib.parse import quote

import qrcode
from slugify import slugify


def generate_client_password(length: int = 12) -> str:
    """
    Generate a secure random password for client.
    
    Args:
        length: Password length (default 12)
        
    Returns:
        Secure random password with mix of uppercase, lowercase, digits, and symbols
    """
    if length < 8:
        length = 8
    
    # Character sets
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    symbols = "!@#$%^&*"
    
    # Ensure at least one of each type
    password_chars = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(symbols),
    ]
    
    # Fill remaining with random mix
    all_chars = uppercase + lowercase + digits + symbols
    password_chars.extend(secrets.choice(all_chars) for _ in range(length - 4))
    
    # Shuffle to avoid predictable pattern
    secrets.SystemRandom().shuffle(password_chars)
    
    return "".join(password_chars)


def generate_ca_slug(display_name: str) -> str:
    """
    Generate URL-safe slug from CA display name.
    
    Args:
        display_name: CA's display name (e.g., "Lokesh Dagdiya")
        
    Returns:
        URL-safe slug (e.g., "lokesh-dagdiya")
    """
    return slugify(display_name, lowercase=True, max_length=50)


def generate_qr_code(url: str) -> str:
    """
    Generate QR code for portal URL.
    
    Args:
        url: Portal URL to encode
        
    Returns:
        Base64-encoded PNG image (data:image/png;base64,...)
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"


def generate_whatsapp_share_url(
    portal_url: str,
    username: str,
    password: str,
    ca_name: str,
) -> str:
    """
    Generate WhatsApp share URL with pre-filled message.
    
    Args:
        portal_url: Client portal URL
        username: Client username (phone number)
        password: Client password
        ca_name: CA's display name
        
    Returns:
        WhatsApp share URL (https://wa.me/?text=...)
    """
    message = f"""Welcome to {ca_name} Portal!

Portal: {portal_url}
Username: {username}
Password: {password}

Login to view your documents and messages."""
    
    encoded_message = quote(message)
    return f"https://wa.me/?text={encoded_message}"


def validate_slug(slug: str) -> bool:
    """
    Validate CA slug format.
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not slug:
        return False
    
    if len(slug) > 50:
        return False
    
    # Only lowercase alphanumeric and hyphens
    allowed = set(string.ascii_lowercase + string.digits + "-")
    return all(c in allowed for c in slug)
