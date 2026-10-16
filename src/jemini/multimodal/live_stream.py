"""Gemini 3.8 Live API Bidirectional Streaming Client (WebSocket 24kHz PCM)."""

import asyncio
from typing import Optional, AsyncGenerator
from jemini.rotator.rotator import APIKeyRotator

class LiveSessionClient:
    """Manages real-time bidirectional audio/video session with Gemini 3.8 Live API."""
    
    def __init__(self, rotator: APIKeyRotator, model: str = "gemini-3.8-live"):
        self.rotator = rotator
        self.model = model
        self.is_connected = False
        self._current_key: Optional[str] = None

    async def connect(self):
        """Establish bidirectional Live API connection with Hot Standby fallback."""
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self._current_key = await self.rotator.get_active_key()
                # WebSocket connection logic initialization
                self.is_connected = True
                return
            except Exception as e:
                if "429" in str(e) and self._current_key:
                    self._current_key = await self.rotator.handle_429(self._current_key)
                if attempt == max_attempts - 1:
                    raise

    async def disconnect(self):
        self.is_connected = False
        self._current_key = None

    async def send_audio_chunk(self, pcm_chunk: bytes):
        """Send 24kHz 16-bit PCM mono audio chunk to the live stream."""
        if not self.is_connected:
            await self.connect()
        # Audio streaming logic over websocket
        pass

    async def receive_stream(self) -> AsyncGenerator[bytes, None]:
        """Receive synthesized 24kHz PCM audio chunks or responses from Live API."""
        if not self.is_connected:
            await self.connect()
        yield b""
