"""Operator Control Plane & Approval Service for Jemini.

Allows human-in-the-loop sign-off before public distribution,
managing review submissions, one-click approvals, and video archival.
"""

import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from jemini.operator.models import ReviewStatus, ReviewSubmission
from jemini.publishing.youtube_publisher import (
    PublishingPrivacyStatus,
    YouTubePublisher,
    YouTubeShortMetadata,
)

logger = logging.getLogger(__name__)


class OperatorReviewService:
    """Manages the lifecycle of generated videos awaiting operator decision."""

    def __init__(self, storage_file: Path | str = "output/operator_reviews.json"):
        self.storage_file = Path(storage_file).resolve()
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.archive_dir = self.storage_file.parent / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self._submissions: dict[str, ReviewSubmission] = {}
        self._load()

    def _load(self) -> None:
        if self.storage_file.exists():
            try:
                data = json.loads(self.storage_file.read_text(encoding="utf-8"))
                for item in data:
                    sub = ReviewSubmission.model_validate(item)
                    self._submissions[sub.submission_id] = sub
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to load operator reviews from %s: %s", self.storage_file, exc)

    def _save(self) -> None:
        try:
            items = [s.model_dump(mode="json") for s in self._submissions.values()]
            self.storage_file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist operator reviews to %s: %s", self.storage_file, exc)

    def submit_for_review(
        self,
        video_path: Path | str,
        title: str,
        hook_text: str,
        channel_id: str = "stickman_lab",
        validation_score: float = 9.0,
    ) -> ReviewSubmission:
        """Enrolls a generated video into the operator review queue."""
        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        sub = ReviewSubmission(
            submission_id=submission_id,
            channel_id=channel_id,
            title=title,
            hook_text=hook_text,
            video_path=str(Path(video_path).resolve()),
            validation_score=validation_score,
            status=ReviewStatus.PENDING,
        )
        self._submissions[submission_id] = sub
        self._save()
        logger.info("Submitted video '%s' for operator review (%s)", title, submission_id)
        return sub

    def list_submissions(self, status: ReviewStatus | None = None) -> list[ReviewSubmission]:
        """Returns submissions optionally filtered by status."""
        subs = list(self._submissions.values())
        if status:
            subs = [s for s in subs if s.status == status]
        subs.sort(key=lambda s: s.created_at)
        return subs

    def get_submission(self, submission_id: str) -> ReviewSubmission | None:
        return self._submissions.get(submission_id)

    async def approve(
        self,
        submission_id: str,
        publish_youtube: bool = False,
        mock_mode: bool = False,
    ) -> ReviewSubmission:
        """Approves a video and optionally dispatches it to YouTube Shorts."""
        sub = self._submissions.get(submission_id)
        if not sub:
            msg = f"Submission {submission_id} not found."
            raise ValueError(msg)

        sub.status = ReviewStatus.APPROVED
        sub.decided_at = datetime.now(timezone.utc)

        if publish_youtube:
            publisher = YouTubePublisher()
            meta = YouTubeShortMetadata(
                title=sub.title,
                description=f"{sub.hook_text}\n\nСтворено повністю автономно через рушій Jemini.",
                privacy_status=PublishingPrivacyStatus.PUBLIC,
            )
            pub_res = await publisher.publish_short(
                video_path=sub.video_path,
                metadata=meta,
                channel_id=sub.channel_id,
                mock_mode=mock_mode,
            )
            sub.published_video_id = pub_res.video_id
            logger.info("✓ Approved and published submission %s: %s", submission_id, pub_res.published_url)

        self._save()
        return sub

    def reject(self, submission_id: str, reason: str = "Operator rejection") -> ReviewSubmission:
        """Rejects a video and moves the file to the archive directory."""
        sub = self._submissions.get(submission_id)
        if not sub:
            msg = f"Submission {submission_id} not found."
            raise ValueError(msg)

        sub.status = ReviewStatus.REJECTED
        sub.decided_at = datetime.now(timezone.utc)
        sub.notes = reason

        # Archive file if present
        vpath = Path(sub.video_path)
        if vpath.exists():
            dest = self.archive_dir / vpath.name
            try:
                shutil.move(vpath, dest)
                sub.video_path = str(dest)
                logger.info("Archived rejected video to %s", dest)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to archive video %s: %s", vpath, exc)

        self._save()
        return sub

    def request_revision(self, submission_id: str, notes: str) -> ReviewSubmission:
        """Flags the submission for revision with specific operator feedback."""
        sub = self._submissions.get(submission_id)
        if not sub:
            msg = f"Submission {submission_id} not found."
            raise ValueError(msg)

        sub.status = ReviewStatus.REVISION_REQUESTED
        sub.decided_at = datetime.now(timezone.utc)
        sub.notes = notes
        self._save()
        logger.info("Revision requested for %s: %s", submission_id, notes)
        return sub
