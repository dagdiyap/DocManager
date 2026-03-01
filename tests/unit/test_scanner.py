import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session

from ca_desktop.backend.src.modules.documents.scanner import DocumentIndexer
from ca_desktop.backend.src import models


@pytest.fixture
def mock_db():
    db = MagicMock(spec=Session)

    def mock_refresh(obj):
        obj.id = 1

    db.refresh.side_effect = mock_refresh
    return db


@pytest.fixture
def indexer(mock_db, tmp_path):
    """Create indexer with mocked settings pointing to tmp_path."""
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.documents_root = tmp_path
        indexer = DocumentIndexer(mock_db)
        # Fix root_path to be tmp_path directly for test stability
        indexer.root_path = tmp_path
        return indexer


class TestDocumentScanner:
    def test_scan_multiple_extensions(self, indexer, mock_db, tmp_path):
        """Test scanning finds multiple file types."""
        # Setup folder structure
        client_dir = tmp_path / "9876543210"
        year_dir = client_dir / "2024"
        year_dir.mkdir(parents=True)

        # Create various file types
        (year_dir / "ITR.pdf").write_text("content")
        (year_dir / "Form16.xlsx").write_text("content")
        (year_dir / "PAN.jpg").write_text("content")
        (year_dir / "Photo.png").write_text("content")
        (year_dir / "Ignored.txt").write_text("content")  # Should be ignored

        # Mock DB query to return None (no existing docs)
        mock_db.query.return_value.filter.return_value.first.return_value = None

        stats = indexer.scan_all()

        assert stats["indexed"] == 4  # PDF, XLSX, JPG, PNG
        assert stats["errors"] == 0

        # Verify db.add called 4 times
        assert mock_db.add.call_count == 4

        # Verify correct types extracted
        calls = mock_db.add.call_args_list
        types_found = [c[0][0].document_type for c in calls]
        assert "ITR" in types_found
        assert "Form16" in types_found
        assert "PAN" in types_found
        assert "Photo" in types_found

    def test_scan_mixed_case_types(self, indexer, mock_db, tmp_path):
        """Test scanning handles mixed case filenames correctly."""
        client_dir = tmp_path / "9876543210"
        year_dir = client_dir / "2024"
        year_dir.mkdir(parents=True)

        (year_dir / "Bank_Statement.pdf").write_text("content")

        mock_db.query.return_value.filter.return_value.first.return_value = None

        stats = indexer.scan_all()
        assert stats["indexed"] == 1

        # Check document type preserved case
        new_doc = mock_db.add.call_args[0][0]
        assert new_doc.document_type == "Bank_Statement"

    def test_update_existing_document(self, indexer, mock_db, tmp_path):
        """Test updating existing document if changed."""
        client_dir = tmp_path / "9876543210"
        year_dir = client_dir / "2024"
        year_dir.mkdir(parents=True)

        file_path = year_dir / "ITR.pdf"
        file_path.write_text("new content")

        # Mock existing DB document
        existing_doc = models.Document(
            id=1,
            file_size=0,  # Different size to trigger update
            is_deleted=False,
        )
        mock_db.query.return_value.filter.return_value.first.return_value = existing_doc

        stats = indexer.scan_all()

        assert stats["indexed"] == 1
        assert existing_doc.file_size == file_path.stat().st_size
        assert mock_db.commit.called

    def test_invalid_structure_ignored(self, indexer, tmp_path):
        """Test invalid folders are skipped."""
        # Invalid phone
        (tmp_path / "invalid_phone").mkdir()

        # Valid phone, invalid year
        client_dir = tmp_path / "9876543210"
        client_dir.mkdir()
        (client_dir / "not_a_year").mkdir()

        stats = indexer.scan_all()
        assert stats["indexed"] == 0
        assert stats["errors"] == 0
