"""
AI Gateway entrypoint (Cloud Run ready).

Exposes:
- HTTP health endpoint
- WebSocket /audio streaming endpoint
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from app.gateway import GatewaySession
from app.audio import shutdown_audio

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("ai-gateway")


# ==========================================================
# APP
# ==========================================================

app = FastAPI(title="AI Gateway", version="1.0")


# ==========================================================
# HEALTH CHECK (Cloud Run)
# ==========================================================

@app.get("/health")
async def health():
    return {"status": "ok"}


# ==========================================================
# WEBSOCKET ENTRYPOINT
# ==========================================================

@app.websocket("/audio")
async def audio_endpoint(websocket: WebSocket):
    """
    Main streaming endpoint:
    Ceres <-> AI Gateway <-> VosynCore
    """

    await websocket.accept()

    session = GatewaySession(websocket)

    logger.info(
        "New WebSocket connection accepted"
    )

    try:
        await session.start()

    except WebSocketDisconnect:
        logger.info("Client disconnected")

    except Exception as e:
        logger.error("Unexpected error: %s", e)

    finally:
        await session.stop()


# ==========================================================
# SHUTDOWN HOOK
# ==========================================================

@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean shutdown for Cloud Run.
    """

    logger.info("Shutting down AI Gateway")

    shutdown_audio()
