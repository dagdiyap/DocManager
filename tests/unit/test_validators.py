import pytest
from shared.utils.validators import (
    validate_document_type,
    validate_file_path,
    validate_phone_number,
    validate_year,
    ValidationError,
    PhoneNumberError,
)
from shared.utils.constants import ALLOWED_FILE_EXTENSIONS


class TestValidators:
    def test_validate_document_type_mixed_case(self):
        """Test mixed case document types are allowed."""
        assert validate_document_type("ITR") == "ITR"
        assert validate_document_type("Form16") == "Form16"
        assert validate_document_type("Bank_Statement") == "Bank_Statement"
        assert validate_document_type("gst_return") == "gst_return"

    def test_validate_document_type_invalid(self):
        """Test invalid document types."""
        with pytest.raises(ValidationError):
            validate_document_type("ITR File")  # Spaces not allowed
        with pytest.raises(ValidationError):
            validate_document_type("ITR-2024")  # Hyphens not allowed
        with pytest.raises(ValidationError):
            validate_document_type("ITR@2024")  # Special chars not allowed

    def test_validate_file_path_extensions(self):
        """Test file path validation with allowed extensions."""
        # PDF
        path = validate_file_path("document.pdf", ALLOWED_FILE_EXTENSIONS)
        assert path.suffix == ".pdf"

        # Images
        path = validate_file_path("image.png", ALLOWED_FILE_EXTENSIONS)
        assert path.suffix == ".png"
        path = validate_file_path("photo.jpg", ALLOWED_FILE_EXTENSIONS)
        assert path.suffix == ".jpg"

        # Excel
        path = validate_file_path("sheet.xlsx", ALLOWED_FILE_EXTENSIONS)
        assert path.suffix == ".xlsx"

    def test_validate_file_path_invalid_extension(self):
        """Test invalid extension rejection."""
        with pytest.raises(ValidationError):
            validate_file_path("script.exe", ALLOWED_FILE_EXTENSIONS)

        with pytest.raises(ValidationError):
            validate_file_path("test.py", ALLOWED_FILE_EXTENSIONS)

    def test_validate_file_path_traversal(self):
        """Test path traversal prevention."""
        with pytest.raises(ValidationError):
            validate_file_path("../secret.txt")

        with pytest.raises(ValidationError):
            validate_file_path("documents/../../etc/passwd")

    def test_validate_phone_number(self):
        """Test phone number validation."""
        assert validate_phone_number("9876543210") == "9876543210"
        assert validate_phone_number("+91-9876543210") == "919876543210"

        with pytest.raises(PhoneNumberError):
            validate_phone_number("123")  # Too short

        with pytest.raises(PhoneNumberError):
            validate_phone_number("abc")  # Not digits

    def test_validate_year(self):
        """Test year validation."""
        assert validate_year("2024") == "2024"

        with pytest.raises(ValidationError):
            validate_year("24")  # Too short

        with pytest.raises(ValidationError):
            validate_year("abcd")  # Not digits
