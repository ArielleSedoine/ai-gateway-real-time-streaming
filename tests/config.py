
"""
Configuration for the Ceres simulator.
"""

from __future__ import annotations

import os
from pathlib import Path

# ==========================================================
# PATHS
# ==========================================================

# Directory containing this file (tests/)
TESTS_DIR = Path(__file__).resolve().parent

# ==========================================================
# AI GATEWAY
# ==========================================================

GATEWAY_URL = os.getenv(
    "GATEWAY_URL",
    "wss://ai-gateway-up01-1038404886674.us-east4.run.app/audio",
)

# ==========================================================
# AUDIO
# ==========================================================

SAMPLE_RATE = 48_000

CHANNELS = 1

FRAME_DURATION_MS = 20

# 20 ms @ 48 kHz = 960 samples
FRAME_SIZE = SAMPLE_RATE * FRAME_DURATION_MS // 1000

SAMPLE_WIDTH = 2  # bytes (16-bit PCM)

# ==========================================================
# STREAMING
# ==========================================================

STREAM_REALTIME = True

RECONNECT_DELAY = 5

CONNECT_TIMEOUT = 10

MAX_MESSAGE_SIZE = None

# ==========================================================
# BINARY PROTOCOL
# ==========================================================

# Network byte order (Big Endian)
# uint32 sequence
# uint64 timestamp_ns
HEADER_FORMAT = "!IQ"

HEADER_SIZE = 12

# ==========================================================
# AUTOMATIC WAV DISCOVERY
# ==========================================================

wav_files = sorted(TESTS_DIR.glob("*.wav"))

if not wav_files:
    raise FileNotFoundError(
        f"No .wav file found in '{TESTS_DIR}'.\n"
        "Copy any WAV file into the tests/ directory."
    )

if len(wav_files) > 1:
    raise RuntimeError(
        "Multiple WAV files found:\n"
        + "\n".join(f" - {f.name}" for f in wav_files)
        + "\n\nPlease keep only one WAV file in tests/."
    )

AUDIO_FILE = wav_files[0]

print(f"Using audio file: {AUDIO_FILE.name}")

# ==========================================================
# LOGGING
# ==========================================================

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
)
