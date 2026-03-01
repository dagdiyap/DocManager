"""Main entry point for the CA Desktop Backend."""

from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from shared.utils.logging import get_logger, setup_logging

from ca_desktop.backend.src import config, database
from ca_desktop.backend.src.exceptions import CADesktopError
from ca_desktop.backend.src.middleware.rate_limit import RateLimitMiddleware
from ca_desktop.backend.src.middleware.request_logging import RequestLoggingMiddleware
from ca_desktop.backend.src.routers import (
    auth,
    ca_profile,
    clients,
    compliance,
    documents,
    messaging,
    public,
    reminders,
    reminders_v2,
    tags,
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events."""
    _ = config.get_settings()

    # Initialize Database
    logger.info("Initializing database...")
    database.init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info("Backend shutting down...")


# Setup Logging
settings = config.get_settings()
setup_logging(log_level=settings.log_level, log_file=settings.log_file)

app = FastAPI(title="CA Document Manager - Desktop Backend", version="0.1.0", lifespan=lifespan)


# Exception Handlers
@app.exception_handler(CADesktopError)
async def ca_desktop_exception_handler(request: Request, exc: CADesktopError):
    """Global handler for CA Desktop custom exceptions."""
    logger.error(f"Error: {exc.message} (Code: {exc.error_code})")
    status_code = 500

    # Map common exceptions to status codes
    exception_name = exc.__class__.__name__
    if "NotFound" in exception_name:
        status_code = 404
    elif "Unauthorized" in exception_name:
        status_code = 401
    elif "Invalid" in exception_name or "Mismatch" in exception_name:
        status_code = 400
    elif "Expired" in exception_name:
        status_code = 401
    elif "Forbidden" in exception_name:
        status_code = 403
    elif "AlreadyExists" in exception_name:
        status_code = 409

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with clear messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        errors.append({"field": field, "message": error["msg"]})

    logger.warning(f"Validation error on {request.url.path}: {errors}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "validation_error",
            "message": "Invalid request data",
            "details": errors,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors safely without leaking stack traces."""
    logger.exception(f"Unexpected error on {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Rate Limiting
app.add_middleware(RateLimitMiddleware)

# Request Logging
app.add_middleware(RequestLoggingMiddleware)


# Include Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(clients.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(messaging.router, prefix="/api/v1")
app.include_router(tags.router, prefix="/api/v1")
app.include_router(compliance.router, prefix="/api/v1")
app.include_router(reminders.router, prefix="/api/v1")
app.include_router(reminders_v2.router, prefix="/api/v1")
app.include_router(ca_profile.router, prefix="/api/v1")
app.include_router(public.router, prefix="/api/v1")


@app.get("/", tags=["General"])
def read_root():
    return {"status": "CA Desktop Backend Online"}
