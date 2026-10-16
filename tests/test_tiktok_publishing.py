from pathlib import Path

import pytest

from jemini.publishing.tiktok_publisher import (
    TikTokMetadata,
    TikTokPrivacyStatus,
    TikTokPublisher,
)


def test_tiktok_caption_formatting():
    publisher = TikTokPublisher()

    # Test stickman_lab channel
    cap1 = publisher.format_caption(
        title="Як зламати пентагон за 5 хвилин #Shorts",
        channel_id="stickman_lab",
    )
    assert "Як зламати пентагон за 5 хвилин" in cap1
    assert "#Shorts" not in cap1.split("\n\n")[0]  # Removed from title line
    assert "#Jemini" in cap1
    assert "#Coding" in cap1

    # Test cyber_matrix channel
    cap2 = publisher.format_caption(
        title="Zero-Day Vulnerability Scanning",
        channel_id="cyber_matrix",
        extra_tags=["#Linux", "#Hacking"],
    )
    assert "Zero-Day Vulnerability Scanning" in cap2
    assert "#CyberSecurity" in cap2
    assert "#Hacking" in cap2


def test_tiktok_credentials_discovery(tmp_path: Path):
    fake_session = tmp_path / "tiktok_session.json"
    fake_session.write_text('{"cookies": []}', encoding="utf-8")

    publisher = TikTokPublisher(session_path=fake_session)
    assert publisher.has_credentials() is True


@pytest.mark.asyncio
async def test_tiktok_publish_mock(tmp_path: Path):
    publisher = TikTokPublisher()
    test_video = tmp_path / "mock_tiktok_video.mp4"
    test_video.write_bytes(b"MOCK_TIKTOK_DATA")

    meta = TikTokMetadata(
        title="AI Automation with Jemini",
        privacy_status=TikTokPrivacyStatus.PUBLIC,
    )

    res = await publisher.publish_video(
        video_path=test_video,
        metadata=meta,
        channel_id="cyber_matrix",
        mock_mode=True,
    )

    assert res.success is True
    assert res.status == "PUBLISHED_MOCK"
    assert "AI Automation with Jemini" in res.caption
    assert "#CyberSecurity" in res.caption


@pytest.mark.asyncio
async def test_tiktok_publish_missing_file():
    publisher = TikTokPublisher()
    meta = TikTokMetadata(title="Missing file test")

    res = await publisher.publish_video(
        video_path="non_existent_file.mp4",
        metadata=meta,
        channel_id="stickman_lab",
        mock_mode=False,
    )

    assert res.success is False
    assert res.status == "FAILED"
    assert "not found" in res.error.lower()
