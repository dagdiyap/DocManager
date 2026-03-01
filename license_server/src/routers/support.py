"""Router for remote support and WebSocket communication."""

import datetime
import uuid
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    status,
)
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

from license_server.src import config, models
from license_server.src.database import get_db
from license_server.src.support.websocket_manager import ws_manager

logger = get_logger(__name__)
router = APIRouter(prefix="/support", tags=["Remote Support"])


@router.websocket("/connect/{ca_id}")
async def support_websocket_endpoint(
    websocket: WebSocket, ca_id: str, db: Session = Depends(get_db)
):
    """WebSocket endpoint for CA desktops to connect for remote support."""
    # 1. Verify CA ID
    db_ca = db.query(models.CA).filter(models.CA.id == ca_id).first()
    if not db_ca:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"WebSocket reject: Unknown CA {ca_id}")
        return

    # 2. Register connection
    await ws_manager.connect(ca_id, websocket)

    # 3. Log support session creation
    session_token = str(uuid.uuid4())
    db_session = models.SupportSession(
        ca_id=ca_id,
        session_token=session_token,
        connected_at=datetime.datetime.utcnow(),
        status="active",
    )
    db.add(db_session)
    db.commit()

    try:
        while True:
            # Receive message from CA Desktop
            data = await websocket.receive_json()
            logger.debug(f"Received from CA {ca_id}: {data}")

            # Type: Diagnostics
            if data.get("type") == "diagnostics":
                # Create a record in remote_commands for the "push" response if needed
                # For now let's just log it
                logger.info(
                    f"Diagnostics received from CA {ca_id}: {data.get('payload')}"
                )

            # Type: Approval
            elif data.get("type") == "approval":
                cmd_id = data.get("command_id")
                approved = data.get("approved")
                logger.info(
                    f"Remote command {cmd_id} approval from CA {ca_id}: {approved}"
                )
                # Update DB record if command was tracking in DB
                db_cmd = (
                    db.query(models.RemoteCommand)
                    .filter(models.RemoteCommand.id == cmd_id)
                    .first()
                )
                if db_cmd:
                    db_cmd.approved_by_ca = approved
                    db.commit()

    except WebSocketDisconnect:
        ws_manager.disconnect(ca_id, websocket)
        # Update session status
        db_session.disconnected_at = datetime.datetime.utcnow()
        db_session.status = "closed"
        db.commit()
    except Exception as e:
        logger.error(f"WebSocket error for CA {ca_id}: {str(e)}")
        ws_manager.disconnect(ca_id, websocket)


@router.get("/connected-cas", response_model=list[str])
def get_connected_cas():
    """Get a list of currently online CA IDs."""
    return ws_manager.get_connected_cas()


@router.post("/command/{ca_id}")
async def send_command(
    ca_id: str, payload: dict[str, Any], db: Session = Depends(get_db)
):
    """Push a remote command to a connected CA desktop."""
    if not ws_manager.is_connected(ca_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"CA {ca_id} is not online"
        )

    # Track command in DB
    # We need an active session
    db_session = (
        db.query(models.SupportSession)
        .filter(
            models.SupportSession.ca_id == ca_id,
            models.SupportSession.status == "active",
        )
        .first()
    )

    if not db_session:
        raise HTTPException(status_code=400, detail="No active support session found")

    db_cmd = models.RemoteCommand(
        session_id=db_session.id,
        ca_id=ca_id,
        command_type=payload.get("type", "unknown"),
        command_payload=payload,
    )
    db.add(db_cmd)
    db.commit()
    db.refresh(db_cmd)

    # Prepare message for WS
    ws_message = {
        "type": "command",
        "command_id": db_cmd.id,
        "action": payload.get("type"),
        "payload": payload,
    }

    # Send via WebSocket
    await ws_manager.send_json(ca_id, ws_message)

    return {"status": "command_pushed", "command_id": db_cmd.id}


@router.post("/push-update/{ca_id}")
async def push_update(ca_id: str, version: str, db: Session = Depends(get_db)):
    """Push an application update version to a connected CA desktop."""
    if not ws_manager.is_connected(ca_id):
        raise HTTPException(status_code=404, detail="CA is not online")

    # Get version details
    db_version = (
        db.query(models.AppVersion).filter(models.AppVersion.version == version).first()
    )
    if not db_version:
        raise HTTPException(
            status_code=404, detail=f"Version {version} not found on server"
        )

    payload = {
        "type": "update",
        "version": db_version.version,
        "file_hash": db_version.file_hash,
        "download_url": f"{config.get_settings().license_server_url}/api/v1/support/download/{version}",
        "requires_approval": True,
    }

    return await send_command(ca_id, payload, db)


@router.get("/download/{version}")
def download_app_version(version: str, db: Session = Depends(get_db)):
    """Endpoint for CA desktops to download update files."""
    db_version = (
        db.query(models.AppVersion).filter(models.AppVersion.version == version).first()
    )
    if not db_version:
        raise HTTPException(status_code=404, detail="Version not found")

    from fastapi.responses import FileResponse

    return FileResponse(
        path=db_version.file_path,
        filename=f"CA_DocManager_{version}.exe",
        media_type="application/octet-stream",
    )
