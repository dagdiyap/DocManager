"""Unit tests for invite utilities."""

import re

import pytest

from ca_desktop.backend.src.utils.invite import (
    generate_ca_slug,
    generate_client_password,
    generate_qr_code,
    generate_whatsapp_share_url,
    validate_slug,
)


class TestPasswordGeneration:
    """Test client password generation."""

    def test_password_length(self):
        """Test password has correct length."""
        password = generate_client_password(12)
        assert len(password) == 12

    def test_password_minimum_length(self):
        """Test password enforces minimum length."""
        password = generate_client_password(4)
        assert len(password) == 8  # Should enforce minimum

    def test_password_contains_uppercase(self):
        """Test password contains uppercase letters."""
        password = generate_client_password()
        assert any(c.isupper() for c in password)

    def test_password_contains_lowercase(self):
        """Test password contains lowercase letters."""
        password = generate_client_password()
        assert any(c.islower() for c in password)

    def test_password_contains_digit(self):
        """Test password contains digits."""
        password = generate_client_password()
        assert any(c.isdigit() for c in password)

    def test_password_contains_symbol(self):
        """Test password contains symbols."""
        password = generate_client_password()
        assert any(c in "!@#$%^&*" for c in password)

    def test_password_uniqueness(self):
        """Test passwords are unique."""
        passwords = [generate_client_password() for _ in range(100)]
        assert len(set(passwords)) == 100  # All unique


class TestSlugGeneration:
    """Test CA slug generation."""

    def test_simple_name(self):
        """Test slug from simple name."""
        slug = generate_ca_slug("Lokesh Dagdiya")
        assert slug == "lokesh-dagdiya"

    def test_special_characters(self):
        """Test slug removes special characters."""
        slug = generate_ca_slug("Piyush Rathi & Associates")
        assert slug == "piyush-rathi-associates"

    def test_multiple_spaces(self):
        """Test slug handles multiple spaces."""
        slug = generate_ca_slug("John   Doe")
        assert slug == "john-doe"

    def test_unicode_characters(self):
        """Test slug handles unicode."""
        slug = generate_ca_slug("Ramesh Śarmā")
        assert "ramesh" in slug

    def test_max_length(self):
        """Test slug respects max length."""
        long_name = "A" * 100
        slug = generate_ca_slug(long_name)
        assert len(slug) <= 50

    def test_lowercase(self):
        """Test slug is lowercase."""
        slug = generate_ca_slug("UPPERCASE NAME")
        assert slug.islower()


class TestSlugValidation:
    """Test slug validation."""

    def test_valid_slug(self):
        """Test valid slug passes."""
        assert validate_slug("lokesh-dagdiya") is True

    def test_uppercase_invalid(self):
        """Test uppercase is invalid."""
        assert validate_slug("Lokesh-Dagdiya") is False

    def test_special_chars_invalid(self):
        """Test special characters are invalid."""
        assert validate_slug("lokesh@dagdiya") is False

    def test_spaces_invalid(self):
        """Test spaces are invalid."""
        assert validate_slug("lokesh dagdiya") is False

    def test_empty_invalid(self):
        """Test empty slug is invalid."""
        assert validate_slug("") is False

    def test_too_long_invalid(self):
        """Test too long slug is invalid."""
        assert validate_slug("a" * 51) is False

    def test_numbers_valid(self):
        """Test numbers are valid."""
        assert validate_slug("ca-123") is True


class TestQRCodeGeneration:
    """Test QR code generation."""

    def test_qr_code_format(self):
        """Test QR code returns base64 data URL."""
        url = "https://example.com/ca-lokesh/home"
        qr = generate_qr_code(url)
        assert qr.startswith("data:image/png;base64,")

    def test_qr_code_not_empty(self):
        """Test QR code is not empty."""
        url = "https://example.com/ca-lokesh/home"
        qr = generate_qr_code(url)
        # Should have base64 data after prefix
        base64_data = qr.split(",")[1]
        assert len(base64_data) > 100  # QR codes are reasonably sized

    def test_qr_code_different_urls(self):
        """Test different URLs produce different QR codes."""
        qr1 = generate_qr_code("https://example.com/ca-1")
        qr2 = generate_qr_code("https://example.com/ca-2")
        assert qr1 != qr2


class TestWhatsAppShareURL:
    """Test WhatsApp share URL generation."""

    def test_whatsapp_url_format(self):
        """Test WhatsApp URL has correct format."""
        url = generate_whatsapp_share_url(
            portal_url="https://example.com/ca-lokesh/home",
            username="9876543210",
            password="Test123!@#",
            ca_name="Lokesh & Associates",
        )
        assert url.startswith("https://wa.me/?text=")

    def test_whatsapp_url_contains_portal(self):
        """Test WhatsApp message contains portal URL."""
        portal_url = "https://example.com/ca-lokesh/home"
        url = generate_whatsapp_share_url(
            portal_url=portal_url,
            username="9876543210",
            password="Test123!@#",
            ca_name="Lokesh & Associates",
        )
        # URL-encoded version should be in the message
        assert "example.com" in url

    def test_whatsapp_url_contains_username(self):
        """Test WhatsApp message contains username."""
        url = generate_whatsapp_share_url(
            portal_url="https://example.com/ca-lokesh/home",
            username="9876543210",
            password="Test123!@#",
            ca_name="Lokesh & Associates",
        )
        assert "9876543210" in url

    def test_whatsapp_url_contains_password(self):
        """Test WhatsApp message contains password."""
        password = "Test123!@#"
        url = generate_whatsapp_share_url(
            portal_url="https://example.com/ca-lokesh/home",
            username="9876543210",
            password=password,
            ca_name="Lokesh & Associates",
        )
        # Password should be URL-encoded
        assert "Test123" in url

    def test_whatsapp_url_encoding(self):
        """Test special characters are URL-encoded."""
        url = generate_whatsapp_share_url(
            portal_url="https://example.com/ca-test/home",
            username="9876543210",
            password="Test@123",
            ca_name="Test & Associates",
        )
        # Spaces should be encoded as %20
        assert "%20" in url or "+" in url
        # & should be encoded
        assert "%26" in url or "&" not in url.split("?text=")[1]
