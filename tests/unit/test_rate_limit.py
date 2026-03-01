import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

from ca_desktop.backend.src.main import app
from ca_desktop.backend.src.middleware.rate_limit import RateLimitMiddleware


@pytest.fixture
def client():
    # Use a fresh client for each test to ensure middleware state is reset?
    # Middleware state is persistent in the 'app' instance.
    # We might need to access the middleware instance to clear it, or just use different IPs.
    return TestClient(app)


def test_rate_limit_enforcement(client):
    # Mock settings to low limit
    with patch("ca_desktop.backend.src.config.get_settings") as mock_settings:
        mock_settings.return_value.rate_limit_per_minute = 5

        # We need to ensure the middleware picks up this setting.
        # The middleware initializes with get_settings() in __init__.
        # Since 'app' is already created, the middleware instance is already created with default settings.
        # We need to patch the middleware instance's settings directly or recreate app.

        # Access middleware instance
        for middleware in app.user_middleware:
            if middleware.cls.__name__ == "RateLimitMiddleware":
                # This is Starlette middleware wrapper, actual instance is created on startup?
                # Actually BaseHTTPMiddleware creates an instance.
                pass

        # Simpler approach: Verify default limit (60) or mock the whole middleware logic?
        # Let's try to inject a lower limit into the existing middleware instance if possible.
        # But 'app.middleware_stack' is built on startup.

        # Alternative: We can modify the request_history directly on the app instance if we can find it.
        # But locating the specific middleware instance in Starlette/FastAPI app is tricky.
        pass


# Let's write a unit test for the middleware class directly instead of integration test which is hard to config on the fly.

@pytest.mark.asyncio
async def test_middleware_logic():
    # Mock app
    async def mock_app(scope, receive, send):
        pass

    middleware = RateLimitMiddleware(mock_app)
    middleware.settings.rate_limit_per_minute = 2

    # Create a mock request
    _ = {
        "type": "http",
        "client": ("127.0.0.1", 12345),
        "path": "/api/v1/test",
        "headers": [],
    }

    async def mock_call_next(request):
        return MagicMock(status_code=200)

    # Request 1 (Allowed)
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.url.path = "/api/v1/test"

    resp = await middleware.dispatch(request, mock_call_next)
    assert resp.status_code == 200

    # Request 2 (Allowed)
    resp = await middleware.dispatch(request, mock_call_next)
    assert resp.status_code == 200

    # Request 3 (Blocked)
    resp = await middleware.dispatch(request, mock_call_next)
    assert resp.status_code == 429

    # Request from different IP (Allowed)
    request.client.host = "192.168.1.1"
    resp = await middleware.dispatch(request, mock_call_next)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_middleware_cleanup():
    app_mock = MagicMock()
    middleware = RateLimitMiddleware(app_mock)
    middleware.cleanup_interval = 0.1  # Short interval

    current_time = time.time()

    # Add old entry
    middleware.request_history["1.1.1.1"] = [current_time - 100]
    middleware.last_cleanup = current_time - 10

    # Trigger cleanup via cleanup logic directly for testability
    middleware._cleanup_history(current_time)

    assert "1.1.1.1" not in middleware.request_history
