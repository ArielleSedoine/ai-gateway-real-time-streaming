"""
Audio processing utilities.

Responsibilities:
- Opus decoding
- Audio resampling
"""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import opuslib
import soxr

from app.config import (
    INPUT_SAMPLE_RATE,
    OUTPUT_SAMPLE_RATE,
    CHANNELS,
    THREAD_POOL_SIZE,
)

from app.models import AudioFrame

logger = logging.getLogger(__name__)

# ==========================================================
# THREAD POOL
# ==========================================================

worker_pool = ThreadPoolExecutor(
    max_workers=THREAD_POOL_SIZE
)


# ==========================================================
# DECODER
# ==========================================================

def create_decoder() -> opuslib.Decoder:
    """
    Create one Opus decoder.

    One decoder must be created per client.
    """
    logger.info(
        "Creating Opus decoder (%d Hz, %d channel(s))",
        INPUT_SAMPLE_RATE,
        CHANNELS,
    )

    return opuslib.Decoder(
        INPUT_SAMPLE_RATE,
        CHANNELS,
    )


# ==========================================================
# OPUS DECODING
# ==========================================================

def decode_opus(
    decoder: opuslib.Decoder,
    frame: AudioFrame,
    frame_size: int,
) -> np.ndarray:
    """
    Decode one Opus frame into PCM int16.
    """
    logger.debug(
        "Decoding Opus frame (%d bytes)",
        len(frame.opus_payload),
    )

    pcm = decoder.decode(
        frame.opus_payload,
        frame_size=frame_size,
    )

    pcm_array = np.frombuffer(
        pcm,
        dtype=np.int16,
    )

    logger.info(
        "Decoded Opus -> %d PCM samples (%d bytes)",
        len(pcm_array),
        len(pcm),
    )

    return pcm_array


# ==========================================================
# RESAMPLING
# ==========================================================

def _resample_sync(
    pcm: np.ndarray,
) -> np.ndarray | None:
    """
    CPU-intensive synchronous resampling.
    """

    if pcm is None or pcm.size == 0:
        logger.warning(
            "Received empty PCM buffer for resampling."
        )
        return None

    logger.debug(
        "Resampling %d -> %d Hz",
        INPUT_SAMPLE_RATE,
        OUTPUT_SAMPLE_RATE,
    )

    resampled = soxr.resample(
        pcm,
        INPUT_SAMPLE_RATE,
        OUTPUT_SAMPLE_RATE,
    ).astype(np.int16)

    logger.info(
        "Resampled %d -> %d samples",
        len(pcm),
        len(resampled),
    )

    return resampled
    

async def resample(
    pcm: np.ndarray,
) -> np.ndarray | None:
    """
    Run resampling in the thread pool.
    """

    loop = asyncio.get_running_loop()

    return await loop.run_in_executor(
        worker_pool,
        _resample_sync,
        pcm,
    )


# ==========================================================
# COMPLETE PIPELINE
# ==========================================================

async def process_audio(
    decoder: opuslib.Decoder,
    frame: AudioFrame,
    frame_size: int,
) -> np.ndarray | None:
    """
    Complete audio pipeline.

    AudioFrame
        ↓
    Decode Opus
        ↓
    PCM 48 kHz
        ↓
    Resample
        ↓
    PCM 16 kHz
    """

    logger.info(
        "Starting audio processing pipeline (frame=%d)",
        frame.sequence,
    )

    pcm_48k = decode_opus(
        decoder,
        frame,
        frame_size,
    )

    pcm_16k = await resample(
        pcm_48k,
    )
    if pcm_16k is not None:

        logger.info(
            "Frame %d processed successfully (%d samples @ %d Hz)",
            frame.sequence,
            len(pcm_16k),
            OUTPUT_SAMPLE_RATE,
        )

    return pcm_16k


# ==========================================================
# CLEANUP
# ==========================================================

def shutdown_audio()-> None:
    """
    Shutdown audio thread pool.
    """
    logger.info(
        "Shutting down audio worker pool"
    )

    worker_pool.shutdown(
        wait=True,
    )
