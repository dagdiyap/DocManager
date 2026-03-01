import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from shared.utils.logging import LogContext, get_logger
from starlette.middleware.base import BaseHTTPMiddleware

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log requests with context and timing."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Context for all logs in this request
        context = {
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
        }

        with LogContext(logger, **context):
            logger.info(f"Request started: {request.method} {request.url.path}")

            try:
                response = await call_next(request)
                process_time = (time.time() - start_time) * 1000

                logger.info(
                    f"Request completed: {response.status_code} "
                    f"in {process_time:.2f}ms"
                )
                response.headers["X-Request-ID"] = request_id
                return response
            except Exception as e:
                process_time = (time.time() - start_time) * 1000
                logger.error(
                    f"Request failed: {str(e)} in {process_time:.2f}ms",
                    exc_info=True,
                )
                raise
