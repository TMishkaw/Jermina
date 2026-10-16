from pathlib import Path

import pytest

from jemini.publishing.youtube_publisher import (
    PublishingPrivacyStatus,
    YouTubePublisher,
    YouTubeShortMetadata,
)


def test_youtube_metadata_formatting():
    publisher = YouTubePublisher()
    
    title1 = publisher._format_shorts_title("Як створити ШІ відео")
    assert title1 == "Як створити ШІ відео #Shorts"
    
    title2 = publisher._format_shorts_title("ШІ Відео #shorts на каналі")
    assert title2 == "ШІ Відео #shorts на каналі"
    assert len(title2) <= 100


def test_youtube_credentials_discovery(tmp_path: Path):
    fake_secret = tmp_path / "client_secret.json"
    fake_secret.write_text('{"installed": {}}', encoding="utf-8")
    
    publisher = YouTubePublisher(client_secrets_path=fake_secret)
    assert publisher.has_credentials() is True


@pytest.mark.asyncio
async def test_youtube_publish_short_mock(tmp_path: Path):
    publisher = YouTubePublisher()
    test_video = tmp_path / "sample_short.mp4"
    test_video.write_bytes(b"MOCK_MP4_CONTENT")
    
    metadata = YouTubeShortMetadata(
        title="Автономний ШІ ролик",
        description="Згенеровано двигуном Jemini",
        privacy_status=PublishingPrivacyStatus.UNLISTED,
    )
    
    res = await publisher.publish_short(
        video_path=test_video,
        metadata=metadata,
        channel_id="stickman_lab",
        mock_mode=True,
    )
    
    assert res.video_id == "mock_shorts_yt123"
    assert "https://youtube.com/shorts/" in res.shorts_url
    assert res.privacy_status == "unlisted"
    assert "#Shorts" in res.title


@pytest.mark.asyncio
async def test_youtube_publish_missing_file():
    publisher = YouTubePublisher()
    metadata = YouTubeShortMetadata(title="Sample")

    with pytest.raises(FileNotFoundError, match="Video file not found"):
        await publisher.publish_short(video_path="non_existent.mp4", metadata=metadata)


@pytest.mark.asyncio
async def test_youtube_publish_widescreen_mock(tmp_path: Path):
    publisher = YouTubePublisher()
    test_video = tmp_path / "sample_widescreen.mp4"
    test_video.write_bytes(b"MOCK_MP4_WIDESCREEN")

    metadata = YouTubeShortMetadata(
        title="Повний 16:9 ролик про ШІ архітектуру",
        description="Повний огляд Jemini двигуна",
        privacy_status=PublishingPrivacyStatus.UNLISTED,
    )

    res = await publisher.publish_video(
        video_path=test_video,
        metadata=metadata,
        is_short=False,
        channel_id="cyber_matrix",
        mock_mode=True,
    )

    assert res.video_id == "mock_video_yt16x9"
    assert "https://youtube.com/watch?v=" in res.watch_url
    assert "#Shorts" not in res.title
    assert res.published_url == res.watch_url

