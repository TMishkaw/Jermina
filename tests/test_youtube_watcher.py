"""Unit tests for YouTube Verification Watcher."""

import pytest

from jemini.publishing.youtube_watcher import (
    YouTubeLiveVideoItem,
    YouTubeVerificationReport,
    YouTubeVerificationWatcher,
)


def test_youtube_watcher_models():
    """Validates schemas for live video item and verification report."""
    item = YouTubeLiveVideoItem(
        video_id="v_test1",
        title="Test Short #Shorts",
        published_at="2026-10-16T19:00:00Z",
        duration_seconds=45.0,
        privacy_status="public",
        view_count=100,
        is_short=True,
    )
    assert item.is_short is True
    assert item.privacy_status == "public"

    report = YouTubeVerificationReport(
        channel_id="UC1ol6l3KL3sgmLPiwQy2QTA",
        channel_title="Jermina AI Studio",
        subscriber_count=39,
        total_view_count=14176,
        total_video_count=217,
        latest_uploads=[item],
        system_health="HEALTHY",
    )
    assert report.system_health == "HEALTHY"
    assert len(report.latest_uploads) == 1


@pytest.mark.asyncio
async def test_youtube_watcher_mock_mode():
    """Verifies that watcher executes cleanly in mock mode without network calls."""
    watcher = YouTubeVerificationWatcher()
    report = await watcher.verify_channel_publications(
        channel_id="UC1ol6l3KL3sgmLPiwQy2QTA",
        recent_limit=3,
        mock_mode=True,
    )
    assert report.system_health == "HEALTHY"
    assert report.channel_id == "UC1ol6l3KL3sgmLPiwQy2QTA"
    assert len(report.latest_uploads) >= 1
