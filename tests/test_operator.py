"""Unit tests for Operator Review Service and One-Click Approval Plane."""

import pytest

from jemini.operator.models import ReviewStatus
from jemini.operator.review_service import OperatorReviewService


@pytest.mark.asyncio
async def test_operator_review_approval_lifecycle(tmp_path):
    storage = tmp_path / "operator_reviews.json"
    service = OperatorReviewService(storage_file=storage)

    # Fake generated video file
    vid_file = tmp_path / "sample_short.mp4"
    vid_file.write_text("dummy video content")

    # 1. Submit for review
    sub = service.submit_for_review(
        video_path=vid_file,
        title="Viral AI Coding Short",
        hook_text="СТОП! ШІ ВЖЕ ПИШЕ КОД?!",
        channel_id="stickman_lab",
        validation_score=9.4,
    )
    assert sub.status == ReviewStatus.PENDING
    assert sub.submission_id.startswith("sub_")

    # 2. List pending
    pending = service.list_submissions(status=ReviewStatus.PENDING)
    assert len(pending) == 1
    assert pending[0].submission_id == sub.submission_id

    # 3. Approve without YouTube upload
    approved = await service.approve(sub.submission_id, publish_youtube=False)
    assert approved.status == ReviewStatus.APPROVED
    assert approved.decided_at is not None

    # 4. Approve with mock YouTube upload
    approved_with_yt = await service.approve(
        sub.submission_id,
        publish_youtube=True,
        mock_mode=True,
    )
    assert approved_with_yt.status == ReviewStatus.APPROVED
    assert approved_with_yt.published_video_id == "mock_shorts_yt123"


def test_operator_reject_and_archive(tmp_path):
    storage = tmp_path / "operator_reviews.json"
    service = OperatorReviewService(storage_file=storage)

    vid_file = tmp_path / "to_reject.mp4"
    vid_file.write_text("flawed video content")

    sub = service.submit_for_review(
        video_path=vid_file,
        title="Low Retention Short",
        hook_text="Банальний вступ",
        channel_id="stickman_lab",
        validation_score=6.2,
    )

    # Reject
    rejected = service.reject(sub.submission_id, reason="Hook is too passive")
    assert rejected.status == ReviewStatus.REJECTED
    assert rejected.notes == "Hook is too passive"

    # Verify moved to archive
    assert not vid_file.exists()
    assert (service.archive_dir / "to_reject.mp4").exists()
