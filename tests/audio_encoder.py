"""
Audio encoder used by the Ceres simulator.

Responsibilities:
- Load a WAV file
- Split into 20 ms frames
- Encode each frame to Opus
"""

from __future__ import annotations

from pathlib import Path
import wave

import opuslib

from tests.config import (
    AUDIO_FILE,
    SAMPLE_RATE,
    CHANNELS,
    FRAME_SIZE,
)


# ==========================================================
# AUDIO ENCODER
# ==========================================================

class AudioEncoder:
    """
    Encode PCM WAV audio into Opus frames.
    """

    def __init__(self) -> None:

        self.encoder = opuslib.Encoder(
            SAMPLE_RATE,
            CHANNELS,
            opuslib.APPLICATION_AUDIO,
        )

    # ------------------------------------------------------

    def encode_file(
        self,
        filename: str | Path = AUDIO_FILE,
    ):
        """
        Read a WAV file and yield one Opus frame
        every 20 ms.

        Parameters
        ----------
        filename:
            Path to a mono 48 kHz 16-bit PCM WAV file.

        Yields
        ------
        bytes
            One Opus frame.
        """

        filename = Path(filename)

        if not filename.exists():
            raise FileNotFoundError(
                f"Audio file not found: {filename}"
            )

        with wave.open(str(filename), "rb") as wav:

            if wav.getframerate() != SAMPLE_RATE:
                raise ValueError(
                    f"Expected {SAMPLE_RATE} Hz, "
                    f"got {wav.getframerate()} Hz."
                )

            if wav.getnchannels() != CHANNELS:
                raise ValueError(
                    f"Expected mono audio ({CHANNELS} channel), "
                    f"got {wav.getnchannels()}."
                )

            if wav.getsampwidth() != 2:
                raise ValueError(
                    "Expected 16-bit PCM WAV."
                )

            while True:

                pcm = wav.readframes(FRAME_SIZE)

                if not pcm:
                    break

                expected_size = FRAME_SIZE * 2

                if len(pcm) < expected_size:
                    pcm += b"\x00" * (
                        expected_size - len(pcm)
                    )

                opus_frame = self.encoder.encode(
                    pcm,
                    FRAME_SIZE,
                )

                yield opus_frame
