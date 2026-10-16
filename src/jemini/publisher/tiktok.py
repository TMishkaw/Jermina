"""TikTok publisher for vertical short-form video content."""

from jemini.publisher.base import BasePublisher, PublicationPayload, PublicationResult


class TikTokPublisher(BasePublisher):
    """Handles publishing vertical video content to TikTok."""

    def __init__(self, session_config_path: str = "config/tiktok_session.json"):
        self.session_config_path = session_config_path

    async def publish(self, payload: PublicationPayload) -> PublicationResult:
        return PublicationResult(
            success=True,
            platform="tiktok",
            remote_id=f"tt_mock_{hash(payload.title) % 100000}",
            url=f"https://www.tiktok.com/@channel/video/tt_mock_{hash(payload.title) % 100000}",
        )
