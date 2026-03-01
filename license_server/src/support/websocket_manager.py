"""WebSocket connection manager for remote support."""

from typing import Any

from fastapi import WebSocket
from shared.utils.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manages WebSocket connections from CA desktops for remote support."""

    def __init__(self):
        # Map ca_id to a list of active websocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, ca_id: str, websocket: WebSocket):
        """Accept a connection and register the CA desktop."""
        await websocket.accept()
        if ca_id not in self.active_connections:
            self.active_connections[ca_id] = []
        self.active_connections[ca_id].append(websocket)
        logger.info(
            f"CA {ca_id} connected via WebSocket. Total connections for CA: {len(self.active_connections[ca_id])}"
        )

    def disconnect(self, ca_id: str, websocket: WebSocket):
        """Remove a connection."""
        if ca_id in self.active_connections:
            if websocket in self.active_connections[ca_id]:
                self.active_connections[ca_id].remove(websocket)
            if not self.active_connections[ca_id]:
                del self.active_connections[ca_id]
        logger.info(f"CA {ca_id} disconnected.")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to a specific websocket."""
        await websocket.send_text(message)

    async def send_json(self, ca_id: str, message: dict[str, Any]):
        """Send JSON message to all active connections for a CA."""
        if ca_id in self.active_connections:
            for connection in self.active_connections[ca_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message to CA {ca_id}: {str(e)}")

    async def broadcast(self, message: str):
        """Broadcast message to all connected CAs."""
        for ca_connections in self.active_connections.values():
            for connection in ca_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    pass

    def get_connected_cas(self) -> list[str]:
        """Get list of currently connected CA IDs."""
        return list(self.active_connections.keys())

    def is_connected(self, ca_id: str) -> bool:
        """Check if a specific CA is connected."""
        return ca_id in self.active_connections


# Singleton instance
ws_manager = WebSocketManager()
