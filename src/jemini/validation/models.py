"""Pydantic v2 data models for Media & Component Validation Cards."""

from enum import Enum

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    PASSED = "passed"
    NEEDS_CORRECTION = "needs_correction"
    CRITICAL_FAIL = "critical_fail"


class ValidationTargetType(str, Enum):
    VIDEO = "video"
    AUDIO_VOICE = "audio_voice"
    SCRIPT = "script"
    CODE_COMPONENT = "code_component"


class ValidationIntent(BaseModel):
    title: str
    target_type: ValidationTargetType
    expected_duration_seconds: float | None = None
    target_emotion: str | None = None
    tone_of_voice: str | None = None
    key_points: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class ValidationCard(BaseModel):
    """Structured inspection report produced by the Virtual Art Director."""

    target_type: ValidationTargetType
    status: ValidationStatus
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall compliance score from 0.0 to 10.0")
    passed_criteria: list[str] = Field(default_factory=list)
    detected_issues: list[str] = Field(default_factory=list)
    actionable_recommendations: list[str] = Field(default_factory=list)
    suggested_correction_prompt: str | None = None
    iteration: int = 1
    media_path: str | None = None


class LiveReviewResult(BaseModel):
    """Multimodal streaming audit verdict from Gemini 3.8 Live API."""

    video_path: str
    duration_seconds: float
    frames_streamed: int
    audio_streamed_seconds: float
    status: ValidationStatus
    overall_score: float = Field(ge=0.0, le=10.0, description="Overall compliance score from 0.0 to 10.0")
    hook_evaluation: str = Field(description="Analysis of first 3 seconds hook visual & audio engagement")
    voice_acting_evaluation: str = Field(description="Golden Acting Standard compliance, emotion, natural delivery")
    visual_flow_evaluation: str = Field(description="Typography, pacing, artifacts, visual coherence")
    animation_evaluation: str = Field(default="", description="Smoothness of stickman animation, gesture variety, lip-sync coordination, no freezing")
    design_typography_evaluation: str = Field(default="", description="Typography readability on 1080x1920 mobile viewport, HUD hierarchy, contrast, color palette")
    style_benchmark_evaluation: str = Field(default="", description="Comparison with top-tier modern viral formats like Fireship, Hormozi dynamic captions, MrBeast pacing")
    self_evolution_rules: list[str] = Field(default_factory=list, description="Actionable negative or positive production constraints extracted for autonomous self-improvement")
    intent_discrepancies: str = Field(description="Comparison between expected intent and actual output")
    actionable_improvements: list[str] = Field(default_factory=list, description="Concrete suggestions for refinement")
    full_review_transcript: str = Field(description="Raw commentary received from Gemini Live API session")

