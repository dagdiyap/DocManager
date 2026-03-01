"""Main entry point for the License Server FastAPI application."""

from datetime import datetime

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from shared.crypto import RSAKeyManager
from shared.utils.logging import setup_logging

from license_server.src import config, database
from license_server.src.middleware.request_logging import RequestLoggingMiddleware
from license_server.src.routers import ca, license, support

# 1. Setup logging
settings = config.get_settings()
logger = setup_logging(log_level=settings.log_level, log_file=settings.log_file)

# 2. Create FastAPI app
app = FastAPI(
    title="CA Document Manager - License Authority",
    description="Offline-controlled licensing server for Chartered Accountants",
    version="0.1.0",
)

# 3. Add Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)


# 4. Startup Event
@app.on_event("startup")
def startup_event():
    """Perform startup tasks: DB init and RSA key generation."""
    logger.info("Starting License Server...")

    # Initialize Database
    database.init_db()

    # Ensure RSA Keys exist
    key_manager = RSAKeyManager(settings.private_key_path.parent)
    if not key_manager.keys_exist():
        logger.info("RSA Keys not found. Generating new keypair...")
        key_manager.generate_keypair()
        logger.info(f"Keys generated at {settings.private_key_path.parent}")
    else:
        logger.info(f"Using existing RSA keys from {settings.private_key_path.parent}")


# 5. Root & Health Check
@app.get("/", tags=["General"])
def read_root():
    return {
        "app": "CA Document Manager - License Server",
        "status": "online",
        "timestamp": datetime.utcnow(),
    }


@app.get("/status", tags=["General"])
def get_status(db=Depends(database.get_db)):
    """Check server health and database connectivity."""
    db_ok = False
    try:
        from sqlalchemy import text

        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")

    return {
        "status": "online",
        "version": "0.1.0",
        "db_connected": db_ok,
        "timestamp": datetime.utcnow(),
    }


# 6. Include Routers
app.include_router(ca.router, prefix="/api/v1")
app.include_router(license.router, prefix="/api/v1")
app.include_router(support.router, prefix="/api/v1")


# 7. Error Handling (Placeholder - can be expanded)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {str(exc)}")
    return Response(
        content='{"detail": "Internal Server Error"}',
        status_code=500,
        media_type="application/json",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
