"""
Ceres receiver module.

Responsibilities:
- Receive binary Opus frames from Ceres
- Parse protocol header (sequence + timestamp)
- Build AudioFrame objects
- Push them into Gateway queue
"""

from __future__ import annotations

import logging
import struct

from fastapi import WebSocketDisconnect

from app.models import AudioFrame, ConnectionContext

logger = logging.getLogger(__name__)


# ==========================================================
# PROTOCOL FORMAT
# ==========================================================

# Ceres sends:
#
# uint32 sequence
# uint64 timestamp_ns
# bytes  opus_payload
#
# Header size = 12 bytes

HEADER_FORMAT = "!IQ"

HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


# ==========================================================
# RECEIVER
# ==========================================================

async def receive_from_ceres(
    context: ConnectionContext,
) -> None:
    """
    Receive Opus packets from Ceres and push them into the
    Gateway processing queue.
    """

    ws = context.client_ws

    logger.info(
        "[%s] Ceres receiver started",
        context.session_id,
    )

    try:

        while context.running:

            # --------------------------------------------------
            # RECEIVE BINARY PACKET
            # --------------------------------------------------

            raw = await ws.receive_bytes()

            logger.info(
                "[%s] Received packet (%d bytes)",
                context.session_id,
                len(raw),
            )

            context.stats.frames_received += 1
            context.stats.bytes_received += len(raw)

            # --------------------------------------------------
            # VALIDATE PACKET SIZE
            # --------------------------------------------------

            if len(raw) < HEADER_SIZE:

                logger.warning(
                    "[%s] Invalid packet size: %d bytes",
                    context.session_id,
                    len(raw),
                )

                context.stats.frames_dropped += 1
                continue

            # --------------------------------------------------
            # PARSE HEADER
            # --------------------------------------------------

            try:

                sequence, timestamp_ns = struct.unpack(
                    HEADER_FORMAT,
                    raw[:HEADER_SIZE],
                )

                opus_payload = raw[HEADER_SIZE:]

                logger.info(
                    "[%s] Parsed frame | seq=%d | timestamp=%d | opus=%d bytes",
                    context.session_id,
                    sequence,
                    timestamp_ns,
                    len(opus_payload),
                )

            except Exception as e:

                logger.exception(
                    "[%s] Failed to parse packet",
                    context.session_id,
                )

                context.stats.decode_errors += 1
                continue

            # --------------------------------------------------
            # BUILD AUDIO FRAME
            # --------------------------------------------------

            frame = AudioFrame(
                sequence=sequence,
                timestamp_ns=timestamp_ns,
                opus_payload=opus_payload,
            )

            logger.debug(
                "[%s] AudioFrame created (seq=%d)",
                context.session_id,
                sequence,
            )

            # --------------------------------------------------
            # QUEUE MANAGEMENT
            # --------------------------------------------------

            if context.queue.full():

                logger.warning(
                    "[%s] Queue full (%d). Dropping oldest frame.",
                    context.session_id,
                    context.queue.qsize(),
                )

                try:
                    context.queue.get_nowait()
                    context.stats.frames_dropped += 1

                except Exception:
                    pass

            await context.queue.put(frame)

            logger.info(
                "[%s] Frame %d queued (queue size=%d)",
                context.session_id,
                sequence,
                context.queue.qsize(),
            )

    except WebSocketDisconnect:

        logger.info(
            "[%s] Ceres disconnected",
            context.session_id,
        )

    except Exception:

        logger.exception(
            "[%s] Ceres receiver crashed",
            context.session_id,
        )

    finally:

        context.running = False

        logger.info(
            "[%s] Ceres receiver stopped",
            context.session_id,
        )
