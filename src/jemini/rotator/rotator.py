"""Centralized Gemini API Key Rotator & Quota Manager with Hot Standby."""

import time
import asyncio
from typing import List, Dict, Optional
from jemini.core.exceptions import QuotaExceededException

class KeyState:
    def __init__(self, key: str):
        self.key = key
        self.is_active = True
        self.blocked_until: float = 0.0
        self.error_count: int = 0
        self.success_count: int = 0
        self.last_used: float = 0.0

    @property
    def is_available(self) -> bool:
        return self.is_active and time.time() >= self.blocked_until

    def mark_rate_limited(self, cooldown_seconds: float = 60.0):
        self.blocked_until = time.time() + cooldown_seconds
        self.error_count += 1

    def mark_success(self):
        self.success_count += 1
        self.last_used = time.time()

class APIKeyRotator:
    """Manages pool of Gemini API keys, tracks 429 rate limits, and provides Hot Standby failover."""
    
    def __init__(self, keys: Optional[List[str]] = None, default_cooldown: float = 60.0):
        self._keys: Dict[str, KeyState] = {}
        self.default_cooldown = default_cooldown
        self._lock = asyncio.Lock()
        self._current_index = 0
        
        if keys:
            for k in keys:
                self.add_key(k)

    def add_key(self, key: str) -> None:
        clean_key = key.strip()
        if clean_key and clean_key not in self._keys:
            self._keys[clean_key] = KeyState(clean_key)

    def remove_key(self, key: str) -> None:
        self._keys.pop(key.strip(), None)

    async def get_active_key(self) -> str:
        """Retrieve the next valid, available API key using round-robin and availability check."""
        async with self._lock:
            key_list = list(self._keys.values())
            if not key_list:
                raise QuotaExceededException("No API keys configured in the rotator pool.")

            total = len(key_list)
            for i in range(total):
                idx = (self._current_index + i) % total
                state = key_list[idx]
                if state.is_available:
                    self._current_index = (idx + 1) % total
                    state.mark_success()
                    return state.key

            # All keys are rate-limited or unavailable
            min_wait = min(max(0.0, state.blocked_until - time.time()) for state in key_list)
            raise QuotaExceededException(
                f"All {total} Gemini API keys are currently rate-limited (429). "
                f"Earliest key recovers in {min_wait:.1f}s."
            )

    async def handle_429(self, key: str, retry_after: Optional[float] = None) -> str:
        """Handle 429 Too Many Requests by marking the key and returning a Hot Standby key immediately."""
        async with self._lock:
            cooldown = retry_after if retry_after is not None else self.default_cooldown
            if key in self._keys:
                self._keys[key].mark_rate_limited(cooldown)

        # Hot standby switch
        return await self.get_active_key()

    def get_stats(self) -> List[Dict[str, Any]]:
        return [
            {
                "key_preview": f"{state.key[:4]}...{state.key[-4:]}" if len(state.key) > 8 else "***",
                "is_available": state.is_available,
                "blocked_seconds_left": max(0.0, round(state.blocked_until - time.time(), 1)),
                "success_count": state.success_count,
                "error_count": state.error_count,
            }
            for state in self._keys.values()
        ]
