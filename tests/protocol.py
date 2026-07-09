"""
Binary protocol used by the Ceres simulator.

This module provides the binary packet format used between
Ceres and the AI Gateway.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct
import time

from tests.config import (
    HEADER_FORMAT,
    HEADER_SIZE,
)


# ==========================================================
# AUDIO FRAME
# ==========================================================

@dataclass(slots=True)
class AudioFrame:
    """
    One Ceres audio frame.
    """

    sequence: int

    timestamp_ns: int

    opus_payload: bytes


# ==========================================================
# BUILD PACKET
# ==========================================================

def build_packet(
    sequence: int,
    opus_payload: bytes,
) -> bytes:
    """
    Build one binary packet.

    Format:

        uint32 sequence
        uint64 timestamp_ns
        bytes  opus_payload
    """

    timestamp_ns = time.time_ns()

    header = struct.pack(
        HEADER_FORMAT,
        sequence,
        timestamp_ns,
    )

    return header + opus_payload


# ==========================================================
# PARSE PACKET
# ==========================================================

def parse_packet(
    packet: bytes,
) -> AudioFrame:
    """
    Decode one packet into an AudioFrame.
    """

    if len(packet) < HEADER_SIZE:
        raise ValueError(
            "Packet smaller than protocol header."
        )

    sequence, timestamp_ns = struct.unpack(
        HEADER_FORMAT,
        packet[:HEADER_SIZE],
    )

    opus_payload = packet[HEADER_SIZE:]

    return AudioFrame(
        sequence=sequence,
        timestamp_ns=timestamp_ns,
        opus_payload=opus_payload,
    )
