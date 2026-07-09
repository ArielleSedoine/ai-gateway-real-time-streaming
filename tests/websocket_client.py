"""
WebSocket client for Ceres simulator.

Responsibilities:
- Connect to AI Gateway
- Send Opus frames continuously
- Receive responses in parallel
- Maintain bidirectional streaming
"""

from __future__ import annotations

import asyncio
import logging
import time

import websockets

from tests.config import (
    GATEWAY_URL,
    FRAME_DURATION_MS,
)

from tests.protocol import build_packet
from tests.audio_encoder import AudioEncoder

logger = logging.getLogger(__name__)


# ==========================================================
# CLIENT
# ==========================================================

class WebSocketClient:
    """
    Full duplex Ceres simulator client.
    """

    def __init__(self):
        self.encoder = AudioEncoder()
        self.sequence = 0
        self.running = True

    # ------------------------------------------------------

    async def connect(self):
        """
        Connect to AI Gateway and start streaming.
        """

        logger.info("Connecting to AI Gateway: %s", GATEWAY_URL)

        async with websockets.connect(
            GATEWAY_URL,
            max_size=None,
            ping_interval=20,
            ping_timeout=20,
        ) as ws:

            logger.info("Connected to AI Gateway")

            # Run send + receive concurrently
            await asyncio.gather(
                self._send_loop(ws),
                self._receive_loop(ws),
            )

    # ------------------------------------------------------

    async def _send_loop(self, ws):
        """
        Stream audio frames (20ms Opus packets).
        """

        start_time = time.perf_counter()

        for opus_frame in self.encoder.encode_file():

            if not self.running:
                break

            packet = build_packet(
                self.sequence,
                opus_frame,
            )

            await ws.send(packet)

            logger.info("TX Frame %d (%d bytes)", self.sequence, len(opus_frame))

            self.sequence += 1

            # timing control (real-time 20ms pacing)
            target_time = start_time + (self.sequence * FRAME_DURATION_MS / 1000)
            delay = target_time - time.perf_counter()

            if delay > 0:
                await asyncio.sleep(delay)

        logger.info("Send loop finished")

    # ------------------------------------------------------

    async def _receive_loop(self, ws):
        """
        Receive responses from AI Gateway (VosynCore output).
        """

        try:
            while self.running:

                msg = await ws.recv()

                logger.info("RX %d bytes", len(msg))

        except Exception as e:
            logger.error("Receive error: %s", e)
            self.running = False
