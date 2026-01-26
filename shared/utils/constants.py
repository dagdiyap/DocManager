"""Shared constants for CA Document Manager."""

# Valid document types
VALID_DOCUMENT_TYPES = [
    "ITR",
    "GST_GSTR1",
    "GST_GSTR3B",
    "GST_GSTR9",
    "FORM16",
    "FORM16A",
    "TDS_CERTIFICATE",
    "BALANCE_SHEET",
    "PROFIT_LOSS",
    "AUDIT_REPORT",
    "TAX_AUDIT",
    "ROC_FILING",
    "INCOME_TAX_NOTICE",
    "GST_NOTICE",
    "PAN_CARD",
    "AADHAR",
    "STATEMENT",
    "INVOICE",
    "RECEIPT",
    "OTHER",
]

# File constraints
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB
ALLOWED_FILE_EXTENSIONS = [
    ".pdf",
    ".jpg",
    ".jpeg",
    ".png",
    ".xlsx",
    ".xls",
    ".doc",
    ".docx",
    ".zip",
]

# Token settings
TOKEN_EXPIRY_SECONDS = 600  # 10 minutes
LICENSE_TOKEN_EXPIRY_DAYS = 30  # 30 days default
DEFAULT_LICENSE_DAYS = 30
MAX_LICENSE_DAYS = 365
MIN_LICENSE_DAYS = 1

# Security
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
BCRYPT_ROUNDS = 12

# Rate limiting
MAX_LOGIN_ATTEMPTS = 5
LOGIN_ATTEMPT_WINDOW_SECONDS = 300  # 5 minutes
RATE_LIMIT_PER_MINUTE = 60

# Session settings
SESSION_EXPIRY_HOURS = 24
SESSION_REFRESH_THRESHOLD_HOURS = 6  # Refresh if less than 6 hours remaining

# Phone number
PHONE_MIN_LENGTH = 10
PHONE_MAX_LENGTH = 15

# Database
DB_POOL_SIZE = 5
DB_MAX_OVERFLOW = 10
DB_POOL_TIMEOUT = 30

# Logging
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 30  # Keep 30 days of logs
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# API
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Support mode
SUPPORT_SESSION_TIMEOUT_MINUTES = 30
SUPPORT_HEARTBEAT_INTERVAL_SECONDS = 30
