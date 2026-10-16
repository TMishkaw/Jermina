"""Data models for Operator Review and One-Click Approval Plane."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class ReviewAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REGENERATE_HOOK = "regenerate_hook"


class ReviewSubmission(BaseModel):
    """Artifact bundle awaiting operator sign-off or publishing authorization."""
    submission_id: str
    channel_id: str
    title: str
    hook_text: str
    video_path: str
    validation_score: float = 9.0
    status: ReviewStatus = ReviewStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    decided_at: datetime | None = None
    published_video_id: str | None = None
    notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
