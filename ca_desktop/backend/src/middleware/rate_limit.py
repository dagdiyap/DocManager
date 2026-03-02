import time
from collections import defaultdict

from ca_desktop.backend.src.config import get_settings
from fastapi import Request, status
from shared.utils.logging import get_logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = get_logger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.settings = get_settings()
        # Dictionary to store request timestamps for each IP
        # Format: {ip: [timestamp1, timestamp2, ...]}
        self.request_history = defaultdict(list)
        self.cleanup_interval = 60  # Cleanup every 60 seconds
        self.last_cleanup = time.time()
        self.max_tracked_ips = 1000  # Cap memory usage

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for docs, openapi, and internal WhatsApp endpoints
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/health"]
        skip_prefixes = ["/api/v1/whatsapp/"]
        if request.url.path in skip_paths or any(
            request.url.path.startswith(p) for p in skip_prefixes
        ):
            return await call_next(request)

        client_ip = request.client.host
        current_time = time.time()

        # Cleanup old entries periodically
        if current_time - self.last_cleanup > self.cleanup_interval:
            self._cleanup_history(current_time)
            self.last_cleanup = current_time

        # Get limit from settings
        limit = self.settings.rate_limit_per_minute
        window = 60  # 1 minute window

        # Filter out requests older than the window
        self.request_history[client_ip] = [
            t for t in self.request_history[client_ip] if current_time - t < window
        ]

        # Check limit
        if len(self.request_history[client_ip]) >= limit:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Rate limit exceeded. Please try again later."},
            )

        # Add current request
        self.request_history[client_ip].append(current_time)

        response = await call_next(request)
        return response

    def _cleanup_history(self, current_time):
        """Remove empty entries and stale data."""
        window = 60
        ips_to_remove = []
        for ip, timestamps in self.request_history.items():
            # Keep only recent timestamps
            valid_timestamps = [t for t in timestamps if current_time - t < window]
            if not valid_timestamps:
                ips_to_remove.append(ip)
            else:
                self.request_history[ip] = valid_timestamps

        for ip in ips_to_remove:
            del self.request_history[ip]

        # Hard cap: if too many IPs tracked, drop oldest
        if len(self.request_history) > self.max_tracked_ips:
            sorted_ips = sorted(
                self.request_history.keys(),
                key=lambda ip: max(self.request_history[ip]) if self.request_history[ip] else 0
            )
            for ip in sorted_ips[:len(self.request_history) - self.max_tracked_ips]:
                del self.request_history[ip]
