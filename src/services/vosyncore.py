"""
VosynCore client module.

Responsibilities:
- Maintain WebSocket connection to VosynCore
- Send PCM 16k audio
- Receive responses
- Handle reconnection
"""

from __future__ import annotations

import asyncio
import logging

import websockets

from app.config import (
    VOSYNCORE_URL,
    PING_INTERVAL,
    PING_TIMEOUT,
    RECONNECT_DELAY,
    FRAME_SIZE,
)

from app.audio import process_audio
from app.models import ConnectionContext, AudioFrame


logger = logging.getLogger(__name__)


# ==========================================================
# MAIN LOOP
# ==========================================================

async def vosyncore_loop(
    context: ConnectionContext,
) -> None:
    """
    Maintain persistent connection to VosynCore.

    If VOSYNCORE_URL is not configured,
    VosynCore integration is disabled.
    """

    logger.info(
        "[%s] VosynCore loop started",
        context.session_id,
    )


    # ======================================================
    # MVP MODE
    # ======================================================

    if not VOSYNCORE_URL:

        logger.warning(
            "[%s] VOSYNCORE_URL empty. Running audio pipeline locally.",
            context.session_id,
        )

        await _process_audio_locally(
            context
        )

        return


    # ======================================================
    # PRODUCTION MODE
    # ======================================================

    while context.running:

        try:

            logger.info(
                "[%s] Connecting to VosynCore...",
                context.session_id,
            )


            async with websockets.connect(
                VOSYNCORE_URL,
                ping_interval=PING_INTERVAL,
                ping_timeout=PING_TIMEOUT,
                max_size=None,
            ) as ws:


                context.vosyncore_ws = ws


                logger.info(
                    "[%s] Connected to VosynCore",
                    context.session_id,
                )


                context.stats.reconnect_count += 1


                await asyncio.gather(
                    _send_audio(
                        context,
                        ws,
                    ),

                    _receive_responses(
                        context,
                        ws,
                    ),
                )


        except Exception as e:

            logger.warning(
                "[%s] VosynCore connection error: %s",
                context.session_id,
                e,
            )

            await asyncio.sleep(
                RECONNECT_DELAY
            )



# ==========================================================
# SEND AUDIO
# ==========================================================

async def _send_audio(
    context: ConnectionContext,
    ws,
) -> None:
    """
    Consume Opus frames,
    decode and send PCM16k to VosynCore.
    """

    while context.running:

        frame: AudioFrame = await context.queue.get()


        try:

            pcm_16k = await process_audio(
                context.decoder,
                frame,
                FRAME_SIZE,
            )


            if pcm_16k is None:

                context.stats.frames_dropped += 1
                continue


            await ws.send(
                pcm_16k.tobytes()
            )


            context.stats.frames_sent += 1

            context.stats.bytes_sent += len(
                pcm_16k
            )


        except Exception as e:

            logger.error(
                "[%s] Send error: %s",
                context.session_id,
                e,
            )

            raise


# ==========================================================
# MVP LOCAL AUDIO PIPELINE
# ==========================================================

async def _process_audio_locally(
    context: ConnectionContext,
) -> None:
    """
    MVP mode.

    Consume AudioFrames from Ceres,
    decode Opus,
    resample to PCM16k.

    No VosynCore connection.
    """

    logger.info(
        "[%s] Local audio processing started",
        context.session_id,
    )


    while context.running:

        frame: AudioFrame = await context.queue.get()


        try:

            pcm_16k = await process_audio(
                context.decoder,
                frame,
                FRAME_SIZE,
            )


            if pcm_16k is None:

                context.stats.frames_dropped += 1
                continue


            logger.info(
                "[%s] Frame %d processed locally (%d samples @16kHz)",
                context.session_id,
                frame.sequence,
                len(pcm_16k),
            )


            context.stats.frames_sent += 1

            context.stats.bytes_sent += len(
                pcm_16k.tobytes()
            )


        except Exception as e:

            logger.error(
                "[%s] Local audio processing error: %s",
                context.session_id,
                e,
            )

# ==========================================================
# RECEIVE RESPONSE
# ==========================================================

async def _receive_responses(
    context: ConnectionContext,
    ws,
) -> None:
    """
    Forward VosynCore responses back to Ceres.
    """

    try:

        while context.running:

            msg = await ws.recv()

            await context.client_ws.send_bytes(
                msg
            )


    except Exception as e:

        logger.error(
            "[%s] Receive error: %s",
            context.session_id,
            e,
        )

        raise
