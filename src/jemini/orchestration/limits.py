"""Operational and Technical Limits for Gemini API, Live Streaming, and Video Production."""

from pydantic import BaseModel


class LiveApiLimits(BaseModel):
    """Official Gemini Live API technical and session limits."""
    audio_only_max_minutes: float = 15.0
    audio_video_max_minutes: float = 2.0
    connection_lifetime_minutes: float = 10.0
    audio_token_rate_per_sec: int = 25
    max_safe_scene_words: int = 180  # ~60-70 seconds of speech, safely under any timeout
    sample_rate_output_hz: int = 24000
    sample_rate_input_hz: int = 16000
    video_fps_max: float = 1.0


class RemotionRenderLimits(BaseModel):
    default_concurrency_workers: int = 4
    max_concurrency_workers: int = 8
    recommended_ram_per_worker_mb: int = 1200


class ModelTierLimits(BaseModel):
    flash_lite_rpm: int = 15
    flash_lite_rpd: int = 500
    flash_standard_rpm: int = 5
    flash_standard_rpd: int = 20
    embedding_rpm: int = 100
    embedding_rpd: int = 1000
    live_api_rpm: int | None = None  # Unlimited
    live_api_rpd: int | None = None  # Unlimited
    live_api_tpm: int = 65000


class PipelineLimits:
    """Universal limits repository."""
    LIVE = LiveApiLimits()
    REMOTION = RemotionRenderLimits()
    MODELS = ModelTierLimits()
