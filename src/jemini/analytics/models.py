"""Data models for Audience Retention Analytics and Feedback Loop."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PerformanceTier(str, Enum):
    VIRAL = "viral"
    HEALTHY = "healthy"
    NEEDS_OPTIMIZATION = "needs_optimization"
    CRITICAL = "critical"


class RetentionMetrics(BaseModel):
    """Audience retention metrics gathered from video distribution platforms."""
    video_id: str
    channel_id: str
    total_views: int = Field(default=1000, ge=0)
    retention_at_3s: float = Field(..., ge=0.0, le=100.0, description="Hook retention percentage at 3 seconds")
    retention_at_15s: float = Field(..., ge=0.0, le=100.0, description="Midpoint retention percentage at 15 seconds")
    completion_rate: float = Field(..., ge=0.0, le=100.0, description="Percentage of viewers who watched to the end")
    ctr_percent: float = Field(default=5.0, ge=0.0, le=100.0, description="Click-through rate")
    average_view_duration_seconds: float = Field(default=18.0, ge=0.0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FeedbackAnalysisResult(BaseModel):
    """Actionable insights and negative prompt rules derived from retention analysis."""
    performance_tier: PerformanceTier
    hook_score: float
    pacing_score: float
    retention_score: float
    identified_weaknesses: list[str] = Field(default_factory=list)
    actionable_learnings: list[str] = Field(default_factory=list)
    negative_prompt_rules: list[str] = Field(default_factory=list)
