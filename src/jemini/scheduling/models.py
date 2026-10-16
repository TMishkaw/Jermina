"""Data models for Autonomous Scheduling and Production Queue."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class QueueTaskStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ScoutedTopic(BaseModel):
    """Viral topic scouted for a specific channel niche."""
    title: str
    hook_angle: str
    target_emotion: str = "curiosity, excitement"
    relevance_score: float = Field(default=9.0, ge=0.0, le=10.0)
    keywords: list[str] = Field(default_factory=list)


class ScoutedTopicList(BaseModel):
    topics: list[ScoutedTopic] = Field(default_factory=list)


class ProductionTask(BaseModel):
    """Unit of scheduled video generation in the pipeline."""
    task_id: str
    channel_id: str
    topic: str
    status: QueueTaskStatus = QueueTaskStatus.QUEUED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
    video_path: str | None = None
    validation_score: float | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
