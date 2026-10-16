"""YouTube Shorts Automated Publishing Engine via YouTube Data API v3.

Provides secure OAuth2 authentication, resumable video uploading,
metadata formatting (titles, hashtags, categories), and audit logging.
"""

import asyncio
import datetime
import logging
from enum import Enum
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from pydantic import BaseModel, Field
from sqlalchemy import text

from jemini.publishing.category_selector import CategorySelector, YouTubeCategory
from jemini.storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.readonly",
]
YOUTUBE_UPLOAD_SCOPE = YOUTUBE_SCOPES


class PublishingPrivacyStatus(str, Enum):
    PUBLIC = "public"
    UNLISTED = "unlisted"
    PRIVATE = "private"


class YouTubeShortMetadata(BaseModel):
    """Specification of YouTube Shorts upload metadata."""
    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=lambda: ["Shorts", "AI", "Jemini", "Tech"])
    category_id: str = "auto"  # "auto" for dynamic semantic category selection, or explicit ID ("28", "27", "23")
    privacy_status: PublishingPrivacyStatus = PublishingPrivacyStatus.UNLISTED
    made_for_kids: bool = False


class PublishedVideoResult(BaseModel):
    """Response returned upon successful upload."""
    video_id: str
    shorts_url: str = ""
    watch_url: str = ""
    title: str
    privacy_status: str
    uploaded_at: str
    category_id: str = "28"

    @property
    def published_url(self) -> str:
        return self.shorts_url or self.watch_url


YouTubeVideoMetadata = YouTubeShortMetadata


class YouTubePublisher:
    """Manages YouTube Data API v3 uploads and token credentials."""

    def __init__(
        self,
        client_secrets_path: Path | str | None = None,
        token_path: Path | str | None = None,
    ):
        base = Path(__file__).resolve().parent.parent.parent.parent
        config_dir = base / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        self.client_secrets_file = (
            Path(client_secrets_path)
            if client_secrets_path
            else self._discover_client_secrets(config_dir, base)
        )
        self.token_file = (
            Path(token_path)
            if token_path
            else config_dir / "youtube_token.json"
        )

    def _discover_client_secrets(self, config_dir: Path, base: Path) -> Path:
        candidates = [
            config_dir / "client_secret.json",
            config_dir / "youtube_client_secret.json",
            base / "client_secret.json",
        ]
        for c in candidates:
            if c.exists():
                return c
        return config_dir / "client_secret.json"

    def has_credentials(self) -> bool:
        """Returns True if client secrets or existing token are available."""
        return self.client_secrets_file.exists() or self.token_file.exists()

    def get_authenticated_service(self):
        """Authenticates via OAuth2 and returns YouTube API client."""
        creds = None
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), YOUTUBE_UPLOAD_SCOPE)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Existing token file invalid, re-authenticating: %s", exc)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing expired YouTube OAuth token...")
                creds.refresh(Request())
            else:
                if not self.client_secrets_file.exists():
                    msg = (
                        f"YouTube client secrets not found at {self.client_secrets_file}.\n"
                        "Please download OAuth 2.0 Client ID credentials from Google Cloud Console "
                        "and place them at 'config/client_secret.json'."
                    )
                    raise FileNotFoundError(msg)

                logger.info("Initiating local OAuth2 flow for YouTube...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.client_secrets_file), YOUTUBE_UPLOAD_SCOPE
                )
                creds = flow.run_local_server(port=0)

            # Persist refreshed token
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(creds.to_json(), encoding="utf-8")
            logger.info("Saved authorized token to %s", self.token_file)

        return build("youtube", "v3", credentials=creds)

    def _format_shorts_title(self, raw_title: str) -> str:
        """Ensures title contains #Shorts hashtag and stays within 100 chars."""
        title = raw_title.strip()
        if "#shorts" not in title.lower():
            title = f"{title} #Shorts"
        return title[:100]

    async def _log_upload_to_db(self, channel_id: str, result: PublishedVideoResult) -> None:
        """Records publication audit trail into PostgreSQL."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = text("""
                    INSERT INTO channel_audit_logs (channel_id, action, status, details, created_at)
                    VALUES (:channel_id, :action, :status, :details, NOW());
                """)
                await session.execute(stmt, {
                    "channel_id": channel_id,
                    "action": f"publish_youtube_shorts:{result.video_id}",
                    "status": "published",
                    "details": result.model_dump_json(),
                })
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to record upload audit log: %s", exc)

    async def publish_video(
        self,
        video_path: Path | str,
        metadata: YouTubeShortMetadata,
        is_short: bool = False,
        channel_id: str = "stickman_lab",
        mock_mode: bool = False,
    ) -> PublishedVideoResult:
        """Uploads a video to YouTube (Short or widescreen 16:9) with resumable upload."""
        vid_file = Path(video_path).resolve()
        if not vid_file.exists():
            msg = f"Video file not found: {vid_file}"
            raise FileNotFoundError(msg)

        formatted_title = self._format_shorts_title(metadata.title) if is_short else metadata.title[:100]

        # 1. Resolve YouTube Category dynamically if "auto", empty, or None
        resolved_category_id = metadata.category_id
        if resolved_category_id in ("auto", "", None):
            cat_match = CategorySelector.select_category(
                title=metadata.title,
                description=metadata.description,
                tags=metadata.tags,
            )
            resolved_category_id = cat_match.category_id
            logger.info(
                "✓ Automatically selected YouTube category: %s (%s) | %s",
                resolved_category_id,
                cat_match.category_name,
                cat_match.reasoning,
            )
        else:
            logger.info("Using explicit YouTube category ID: %s", resolved_category_id)

        if mock_mode:
            logger.info("Executing mock YouTube publication for '%s' (is_short=%s)...", formatted_title, is_short)
            video_id = "mock_shorts_yt123" if is_short else "mock_video_yt16x9"
            res = PublishedVideoResult(
                video_id=video_id,
                shorts_url=f"https://youtube.com/shorts/{video_id}" if is_short else "",
                watch_url=f"https://youtube.com/watch?v={video_id}",
                title=formatted_title,
                privacy_status=metadata.privacy_status.value,
                uploaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                category_id=resolved_category_id,
            )
            await self._log_upload_to_db(channel_id, res)
            return res

        # Run blocking network upload in async thread
        def _upload_worker() -> PublishedVideoResult:
            youtube = self.get_authenticated_service()

            body = {
                "snippet": {
                    "title": formatted_title,
                    "description": metadata.description,
                    "tags": metadata.tags,
                    "categoryId": resolved_category_id,
                },
                "status": {
                    "privacyStatus": metadata.privacy_status.value,
                    "selfDeclaredMadeForKids": metadata.made_for_kids,
                },
            }

            media = MediaFileUpload(
                str(vid_file),
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024 * 5,  # 5MB chunks
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            logger.info("Uploading '%s' (%.2f MB) to YouTube (Category ID: %s)...", vid_file.name, vid_file.stat().st_size / (1024 * 1024), resolved_category_id)
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info("Upload progress: %d%%", progress)

            video_id = response.get("id", "unknown_id")
            logger.info("✓ Upload complete! YouTube Video ID: %s", video_id)

            return PublishedVideoResult(
                video_id=video_id,
                shorts_url=f"https://youtube.com/shorts/{video_id}" if is_short else "",
                watch_url=f"https://youtube.com/watch?v={video_id}",
                title=formatted_title,
                privacy_status=metadata.privacy_status.value,
                uploaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                category_id=resolved_category_id,
            )

        result = await asyncio.to_thread(_upload_worker)
        await self._log_upload_to_db(channel_id, result)
        return result

    async def publish_short(
        self,
        video_path: Path | str,
        metadata: YouTubeShortMetadata,
        channel_id: str = "stickman_lab",
        mock_mode: bool = False,
    ) -> PublishedVideoResult:
        """Backwards-compatible convenience wrapper for YouTube Shorts publication."""
        return await self.publish_video(
            video_path=video_path,
            metadata=metadata,
            is_short=True,
            channel_id=channel_id,
            mock_mode=mock_mode,
        )

