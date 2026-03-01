"""Structured logging configuration."""

import json
import logging
import logging.handlers
import sys
import contextvars
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Context variable to store log context
_log_context: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "log_context", default={}
)


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def __init__(self, include_extra: bool = True) -> None:
        """Initialize JSON formatter.

        Args:
            include_extra: Include extra fields in log records
        """
        super().__init__()
        self.include_extra = include_extra

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record

        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Merge context from contextvars
        context = _log_context.get()
        if context:
            log_data.update(context)

        # Add extra fields from record
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in [
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "message",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                ]:
                    # Avoid overwriting context keys if they exist in record extras
                    # (record extras take precedence or vice versa? usually record extras are more specific)
                    if key not in log_data:
                        log_data[key] = value

        # Mask sensitive data
        return json.dumps(mask_sensitive_data(log_data))


def mask_sensitive_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Mask sensitive fields in data.

    Args:
        data: Dictionary that may contain sensitive data

    Returns:
        Dictionary with sensitive fields masked
    """
    masked = data.copy()
    sensitive_keys = [
        "password",
        "secret",
        "token",
        "key",
        "api_key",
        "authorization",
        "cookie",
    ]

    for key, value in masked.items():
        if isinstance(value, str) and any(sensitive in key.lower() for sensitive in sensitive_keys):
            masked[key] = "***REDACTED***"

    return masked


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
    json_format: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 30,
) -> logging.Logger:
    """Setup application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        json_format: Use JSON formatting
        max_bytes: Max log file size before rotation
        backup_count: Number of backup files to keep

    Returns:
        Configured root logger
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    logger.handlers.clear()

    # Create formatter
    formatter: logging.Formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Console handler (always add)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file provided)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a named logger.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to log records."""

    def __init__(self, logger: Optional[logging.Logger] = None, **kwargs: Any) -> None:
        """Initialize log context.

        Args:
            logger: Optional Logger instance (for compatibility, not used for context)
            **kwargs: Context fields to add
        """
        self.context = kwargs
        self.token: Any = None

    def __enter__(self) -> "LogContext":
        """Enter context."""
        current_context = _log_context.get().copy()
        current_context.update(self.context)
        self.token = _log_context.set(current_context)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context."""
        if self.token:
            _log_context.reset(self.token)
