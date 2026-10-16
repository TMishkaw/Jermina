"""Centralized Multi-Provider API Key Rotator & Quota Manager with Hot Standby.

Features:
- Priority for FREE tier keys; fallback to PAID keys.
- Model-specific cooldown tracking: a key rate-limited on heavy models remains usable for light models.
- Shared quota awareness across channels and projects.
- Seamless Hot Standby failover upon 429 (Too Many Requests).
"""

import asyncio
import time
from typing import Any

from pydantic import BaseModel, Field

from jemini.core.exceptions import QuotaExceededException
from jemini.rotator.router import ModelRegistry, TaskTier
from jemini.storage.models import KeyStatus, KeyType


class KeyModelCooldown:
    """Tracks rate-limits per individual model for a given key."""
    def __init__(self):
        # model_name -> timestamp until which model is blocked
        self._cooldowns: dict[str, float] = {}

    def is_available(self, model: str) -> bool:
        blocked_until = self._cooldowns.get(model, 0.0)
        return time.time() >= blocked_until

    def set_cooldown(self, model: str, seconds: float):
        self._cooldowns[model] = time.time() + seconds

    def get_remaining_seconds(self, model: str) -> float:
        blocked_until = self._cooldowns.get(model, 0.0)
        return max(0.0, blocked_until - time.time())

class KeyMetadata(BaseModel):
    key_string: str
    engine: str = "gemini"
    key_type: KeyType = KeyType.FREE
    status: KeyStatus = KeyStatus.ACTIVE
    models_mapping: dict[str, Any] = Field(default_factory=dict)
    total_requests: int = 0
    failed_requests: int = 0
    last_used: float = 0.0

class KeyAcquireResult(BaseModel):
    key_string: str
    model_name: str
    key_type: KeyType
    engine: str

class APIKeyRotator:
    """Universal Key Rotator & Quota Manager."""

    def __init__(self, default_cooldown_seconds: float = 60.0):
        self.default_cooldown_seconds = default_cooldown_seconds
        self._metadata: dict[str, KeyMetadata] = {}
        self._cooldown_trackers: dict[str, KeyModelCooldown] = {}
        self._lock = asyncio.Lock()
        self._round_robin_index = 0

    def register_key(
        self,
        key_string: str,
        engine: str = "gemini",
        key_type: KeyType = KeyType.FREE,
        models_mapping: dict[str, Any] | None = None,
    ) -> None:
        clean = key_string.strip()
        if not clean:
            return
        if clean not in self._metadata:
            self._metadata[clean] = KeyMetadata(
                key_string=clean,
                engine=engine,
                key_type=key_type,
                models_mapping=models_mapping or {},
            )
            self._cooldown_trackers[clean] = KeyModelCooldown()

    def remove_key(self, key_string: str) -> None:
        clean = key_string.strip()
        self._metadata.pop(clean, None)
        self._cooldown_trackers.pop(clean, None)

    async def get_active_key(
        self,
        tier: TaskTier = TaskTier.ROUTINE,
        model_override: str | None = None,
        force_paid: bool = False,
        project_id: str | None = None,
    ) -> KeyAcquireResult:
        """Acquires a valid API key with priority on FREE tier keys and per-model quota checks."""
        model = ModelRegistry.resolve_model(tier, model_override)

        async with self._lock:
            all_keys = list(self._metadata.values())
            if not all_keys:
                raise QuotaExceededException("No API keys configured in the rotator pool.")

            # Filter active keys
            active_keys = [k for k in all_keys if k.status == KeyStatus.ACTIVE]
            if not active_keys:
                raise QuotaExceededException("All API keys are permanently exhausted or banned.")

            # Separate by tier: FREE first, PAID second (unless force_paid requested)
            free_candidates = [k for k in active_keys if k.key_type == KeyType.FREE]
            paid_candidates = [k for k in active_keys if k.key_type == KeyType.PAID]

            search_groups = [paid_candidates] if force_paid else [free_candidates, paid_candidates]

            for group in search_groups:
                if not group:
                    continue
                # Round-robin selection within the group
                total_in_group = len(group)
                for i in range(total_in_group):
                    idx = (self._round_robin_index + i) % total_in_group
                    candidate = group[idx]
                    tracker = self._cooldown_trackers[candidate.key_string]

                    if tracker.is_available(model):
                        self._round_robin_index = (idx + 1) % total_in_group
                        candidate.total_requests += 1
                        candidate.last_used = time.time()
                        return KeyAcquireResult(
                            key_string=candidate.key_string,
                            model_name=model,
                            key_type=candidate.key_type,
                            engine=candidate.engine,
                        )

            # If all candidates for this model are in cooldown
            min_cooldown = min(
                self._cooldown_trackers[k.key_string].get_remaining_seconds(model)
                for k in active_keys
            )
            raise QuotaExceededException(
                f"All {len(active_keys)} keys are in cooldown for model '{model}'. "
                f"Earliest key recovers in {min_cooldown:.1f}s."
            )

    async def handle_429(
        self,
        key_string: str,
        model_name: str,
        retry_after: float | None = None,
        tier: TaskTier = TaskTier.ROUTINE,
    ) -> KeyAcquireResult:
        """Handles 429 Too Many Requests by marking (key, model) cooldown and returning a Hot Standby key."""
        async with self._lock:
            clean = key_string.strip()
            cooldown = retry_after if retry_after is not None else self.default_cooldown_seconds
            
            if clean in self._metadata:
                self._metadata[clean].failed_requests += 1
            if clean in self._cooldown_trackers:
                self._cooldown_trackers[clean].set_cooldown(model_name, cooldown)

        # Immediate Hot Standby switch to another key
        return await self.get_active_key(tier=tier, model_override=model_name)

    def get_stats(self) -> list[dict[str, Any]]:
        stats = []
        for key, meta in self._metadata.items():
            tracker = self._cooldown_trackers[key]
            stats.append({
                "preview": f"{key[:4]}...{key[-4:]}" if len(key) > 8 else "***",
                "engine": meta.engine,
                "tier": meta.key_type.value,
                "status": meta.status.value,
                "total_requests": meta.total_requests,
                "failed_requests": meta.failed_requests,
                "active_cooldowns": {
                    m: round(tracker.get_remaining_seconds(m), 1)
                    for m, _ in tracker._cooldowns.items()
                    if not tracker.is_available(m)
                }
            })
        return stats
