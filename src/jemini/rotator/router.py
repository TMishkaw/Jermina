"""Model Routing and Complexity Differentiation Engine based on official Free-Tier Quotas.

Quotas reference:
- Live API (Gemini 3.8 Live): RPM Unlimited, TPM 65K, RPD Unlimited
- Routine/Lite (Gemini 3.1 Flash Lite / 3.5 Flash Lite): RPM 15, TPM 250K, RPD 500 (25x higher daily quota than standard Flash!)
- Standard Flash (Gemini 2.5/3.8 Flash): RPM 5, TPM 250K, RPD 20
- Embeddings (Gemini Embedding 1/2): RPM 100, TPM 30K, RPD 1K
- Fast Local/Light (Gemma 4 26B/31B): RPM 30, TPM 16K, RPD 14.4K
"""

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel


class TaskTier(str, Enum):
    ROUTINE = "routine"         # High volume, parsing, metadata, basic checks (3.1/3.5 Flash Lite -> 500 RPD)
    COMPLEX = "complex"         # Deep analytics, strategic planning, reasoning (2.5/3.8 Flash / Thinking)
    LIVE_STREAM = "live_stream" # Real-time audio/video streaming & acting voice (Gemini 3.8 Live -> Unlimited RPM/RPD)
    EMBEDDING = "embedding"     # Long-term vector memory embeddings (Gemini Embedding 2 -> 1K RPD)

class ModelQuotaSpec(BaseModel):
    model_name: str
    rpm_limit: int | None  # None = Unlimited
    tpm_limit: int
    rpd_limit: int | None  # None = Unlimited
    category: str

class ModelRegistry:
    """Standard model mapping and official quota specifications."""

    DEFAULT_MODELS: ClassVar[dict[TaskTier, str]] = {
        # Using 3.1 Flash Lite as primary routine model due to massive 500 RPD quota (vs 20 on standard Flash)
        TaskTier.ROUTINE: "gemini-3.1-flash-lite",
        TaskTier.COMPLEX: "gemini-3.8-flash",
        TaskTier.LIVE_STREAM: "gemini-3.8-live",
        TaskTier.EMBEDDING: "gemini-embedding-2",
    }

    QUOTA_SPECS: ClassVar[dict[str, ModelQuotaSpec]] = {
        "gemini-3.8-live": ModelQuotaSpec(
            model_name="gemini-3.8-live",
            rpm_limit=None,
            tpm_limit=65_000,
            rpd_limit=None,
            category="Live API",
        ),
        "gemini-3.8-live-extended-thinking": ModelQuotaSpec(
            model_name="gemini-3.8-live-extended-thinking",
            rpm_limit=None,
            tpm_limit=65_000,
            rpd_limit=None,
            category="Live API",
        ),
        "gemini-3.1-flash-lite": ModelQuotaSpec(
            model_name="gemini-3.1-flash-lite",
            rpm_limit=15,
            tpm_limit=250_000,
            rpd_limit=500,
            category="Text-out models",
        ),
        "gemini-3.5-flash-lite": ModelQuotaSpec(
            model_name="gemini-3.5-flash-lite",
            rpm_limit=15,
            tpm_limit=250_000,
            rpd_limit=500,
            category="Text-out models",
        ),
        "gemini-3.8-flash": ModelQuotaSpec(
            model_name="gemini-3.8-flash",
            rpm_limit=5,
            tpm_limit=250_000,
            rpd_limit=20,
            category="Text-out models",
        ),
        "gemini-2.5-flash": ModelQuotaSpec(
            model_name="gemini-2.5-flash",
            rpm_limit=5,
            tpm_limit=250_000,
            rpd_limit=20,
            category="Text-out models",
        ),
        "gemini-embedding-2": ModelQuotaSpec(
            model_name="gemini-embedding-2",
            rpm_limit=100,
            tpm_limit=30_000,
            rpd_limit=1_000,
            category="Other models",
        ),
        "gemini-3.8-flash-tts": ModelQuotaSpec(
            model_name="gemini-3.8-flash-tts",
            rpm_limit=3,
            tpm_limit=10_000,
            rpd_limit=10,
            category="Multi-modal generative models",
        ),
        "gemini-omni-1.1-flash": ModelQuotaSpec(
            model_name="gemini-omni-1.1-flash",
            rpm_limit=5,
            tpm_limit=250_000,
            rpd_limit=20,
            category="Multi-modal generative models",
        ),
        "gemini-nano-banana-2.1": ModelQuotaSpec(
            model_name="gemini-nano-banana-2.1",
            rpm_limit=5,
            tpm_limit=100_000,
            rpd_limit=50,
            category="Multi-modal generative models",
        ),
        "veo-3.1-generate-preview": ModelQuotaSpec(
            model_name="veo-3.1-generate-preview",
            rpm_limit=2,
            tpm_limit=50_000,
            rpd_limit=10,
            category="Multi-modal generative models",
        ),
        "gemma-4-26b": ModelQuotaSpec(
            model_name="gemma-4-26b",
            rpm_limit=30,
            tpm_limit=16_000,
            rpd_limit=14_400,
            category="Other models",
        ),
    }

    @classmethod
    def resolve_model(cls, tier: TaskTier, override_model: str | None = None) -> str:
        if override_model:
            return override_model
        return cls.DEFAULT_MODELS.get(tier, "gemini-3.1-flash-lite")

    @classmethod
    def get_quota_spec(cls, model_name: str) -> ModelQuotaSpec | None:
        return cls.QUOTA_SPECS.get(model_name)
