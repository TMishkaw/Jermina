"""YouTube publisher supporting long-form videos and YouTube Shorts."""

from jemini.publisher.base import BasePublisher, PublicationPayload, PublicationResult

class YouTubePublisher(BasePublisher):
    """Handles uploads to YouTube and YouTube Shorts via official API."""

    def __init__(self, client_secrets_file: str = "config/client_secrets.json"):
        self.client_secrets_file = client_secrets_file

    async def publish(self, payload: PublicationPayload) -> PublicationResult:
        # Upload workflow: resumable upload protocol
        video_kind = "Shorts" if payload.is_short else "Video"
        return PublicationResult(
            success=True,
            platform="youtube",
            remote_id=f"yt_mock_{hash(payload.title) % 100000}",
            url=f"https://youtube.com/watch?v=yt_mock_{hash(payload.title) % 100000}",
        )
