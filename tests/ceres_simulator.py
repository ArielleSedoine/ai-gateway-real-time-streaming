"""
Ceres simulator (entrypoint).

Streams Opus frames to AI Gateway using full protocol stack.
"""

from __future__ import annotations

import asyncio

from tests.websocket_client import WebSocketClient


# ==========================================================
# MAIN
# ==========================================================

async def main():
    client = WebSocketClient()
    await client.connect()


# ==========================================================
# RUN
# ==========================================================

if __name__ == "__main__":
    asyncio.run(main())
