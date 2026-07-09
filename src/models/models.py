"""
Data models used by the AI Gateway.
"""

from __future__ import annotations

import asyncio
import time

from dataclasses import dataclass, field
from typing import Optional

import opuslib

from fastapi import WebSocket

try:
    # websockets >= 15
    from websockets.asyncio.client import ClientConnection
except ImportError:
    # Fallback pour compatibilité
    ClientConnection = object


# ==========================================================
# AUDIO FRAME
# ==========================================================

@dataclass(slots=True)
class AudioFrame:
    """
    Represents one audio frame received from Ceres.

    Binary protocol:

    uint32 sequence
    uint64 timestamp_ns
    bytes  opus_payload
    """

    sequence: int

    timestamp_ns: int

    opus_payload: bytes


# ==========================================================
# GATEWAY STATISTICS
# ==========================================================

@dataclass(slots=True)
class GatewayStats:
    """
    Runtime statistics for one streaming session.
    """

    frames_received: int = 0

    frames_sent: int = 0

    frames_dropped: int = 0

    decode_errors: int = 0

    reconnect_count: int = 0

    bytes_received: int = 0

    bytes_sent: int = 0

    started_at: float = field(default_factory=time.time)


# ==========================================================
# CONNECTION CONTEXT
# ==========================================================

@dataclass(slots=True)
class ConnectionContext:
    """
    Stores every object related to one client session.
    """

    # Session
    session_id: str

    # FastAPI WebSocket (client <-> AI Gateway)
    client_ws: WebSocket

    # Opus decoder
    decoder: opuslib.Decoder

    # Queue containing AudioFrame objects
    queue: asyncio.Queue[AudioFrame]

    # Connection to VosynCore
    vosyncore_ws: Optional[ClientConnection] = None

    # Running tasks for this session
    tasks: list[asyncio.Task] = field(default_factory=list)

    # Statistics
    stats: GatewayStats = field(default_factory=GatewayStats)

    # Session state
    running: bool = True
