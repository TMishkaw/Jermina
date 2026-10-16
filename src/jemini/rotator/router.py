"""Model Routing and Complexity Differentiation Engine."""

from enum import Enum
from typing import ClassVar


class TaskTier(str, Enum):
    ROUTINE = "routine"         # Quick checks, basic parsing, metadata generation
    COMPLEX = "complex"         # Deep analytics, strategic decisions, script writing
    LIVE_STREAM = "live_stream" # Real-time audio/video streaming (Gemini 3.8 Live API)

class ModelRegistry:
    """Standard model mapping for task tiers."""
    
    DEFAULT_MODELS: ClassVar[dict[TaskTier, str]] = {
        TaskTier.ROUTINE: "gemini-2.5-flash",
        TaskTier.COMPLEX: "gemini-2.5-pro",
        TaskTier.LIVE_STREAM: "gemini-3.8-live",
    }

    @classmethod
    def resolve_model(cls, tier: TaskTier, override_model: str | None = None) -> str:
        if override_model:
            return override_model
        return cls.DEFAULT_MODELS.get(tier, "gemini-2.5-flash")
