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
