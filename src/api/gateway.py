"""
Gateway session orchestrator.

Coordinates one complete streaming session:

Ceres <-> AI Gateway <-> VosynCore
"""

from __future__ import annotations

import asyncio
import logging
import uuid

from fastapi import WebSocket

from app.audio import create_decoder
from app.ceres import receive_from_ceres
from app.models import AudioFrame, ConnectionContext
from app.vosyncore import vosyncore_loop

logger = logging.getLogger(__name__)


class GatewaySession:
    """
    One GatewaySession is created per connected client.
    """

    def __init__(self, websocket: WebSocket):

        self.context = ConnectionContext(
            session_id=str(uuid.uuid4()),
            client_ws=websocket,
            decoder=create_decoder(),
            queue=asyncio.Queue[AudioFrame](),
        )

    async def start(self):
        """
        Start the streaming pipeline.
        """

        logger.info(
            "[%s] Gateway session started",
            self.context.session_id,
        )

        self.context.tasks.extend(
            [
                asyncio.create_task(
                    receive_from_ceres(self.context)
                ),
                asyncio.create_task(
                    vosyncore_loop(self.context)
                ),
            ]
        )

        try:
            await asyncio.gather(*self.context.tasks)

        finally:
            await self.stop()

    async def stop(self):
        """
        Gracefully stop the session.
        """

        if not self.context.running:
            return

        self.context.running = False

        logger.info(
            "[%s] Gateway session stopped",
            self.context.session_id,
        )

        for task in self.context.tasks:
            task.cancel()

        await asyncio.gather(
            *self.context.tasks,
            return_exceptions=True,
        )

        self.context.tasks.clear()

        if self.context.vosyncore_ws is not None:
            try:
                await self.context.vosyncore_ws.close()
            except Exception:
                logger.exception(
                    "[%s] Failed to close VosynCore connection",
                    self.context.session_id,
                )

        try:
            await self.context.client_ws.close()
        except Exception:
            logger.exception(
                "[%s] Failed to close client websocket",
                self.context.session_id,
            )
