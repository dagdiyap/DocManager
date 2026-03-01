"""Secure file streaming logic."""

from pathlib import Path

from ca_desktop.backend.src import config
from fastapi import HTTPException
from fastapi.responses import FileResponse
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class FileStreamer:
    """Handles secure file streaming and path validation."""

    def __init__(self) -> None:
        self.settings = config.get_settings()
        self.docs_root = Path(self.settings.documents_root).resolve()
        self.shared_root = Path(self.settings.shared_files_root).resolve()

    def get_response(self, relative_path: str, is_shared: bool = False) -> FileResponse:
        """Return a FileResponse for the requested path with traversal protection."""
        base_path = self.shared_root if is_shared else self.docs_root

        # 1. Resolve full path
        try:
            full_path = (base_path / relative_path).resolve()
        except Exception as e:
            raise HTTPException(status_code=400, detail="Invalid path format") from e

        # 2. Path Traversal Protection: Ensure resolved path is under base_path
        #    Using is_relative_to() instead of string comparison for cross-platform safety
        try:
            if not full_path.is_relative_to(base_path):
                logger.error(f"Path traversal attempt: {relative_path} (resolved to {full_path})")
                raise HTTPException(status_code=403, detail="Access denied")
        except (ValueError, TypeError):
            logger.error(f"Path traversal attempt: {relative_path} (resolved to {full_path})")
            raise HTTPException(status_code=403, detail="Access denied")

        # 3. Check file existence
        if not full_path.exists() or not full_path.is_file():
            logger.warning(f"File not found: {full_path}")
            raise HTTPException(status_code=404, detail="File not found")

        # 4. Return response
        return FileResponse(
            path=full_path,
            filename=full_path.name,
            media_type="application/octet-stream",
        )
