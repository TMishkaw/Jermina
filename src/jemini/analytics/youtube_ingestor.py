"""YouTube Channel Data Ingestion Engine.

Fetches complete historical archive for a channel: profile stats, all videos
(Shorts and widescreen), view/like metrics, and viewer comment threads.
Zero LLM token consumption (pure YouTube Data API v3).
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.dialects.postgresql import insert

from jemini.storage.database import AsyncSessionLocal
from jemini.storage.models import (
    YouTubeChannelRecord,
    YouTubeCommentRecord,
    YouTubeVideoRecord,
)

logger = logging.getLogger(__name__)


class YouTubeChannelIngestor:
    """Ingests full channel metadata, videos, and comments into PostgreSQL and local JSON."""

    def __init__(
        self,
        token_path: Path | str = "config/youtube_token.json",
        output_dir: Path | str = "data/youtube_dump",
    ):
        self.token_path = Path(token_path).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.service = self._init_youtube_service()

    def _init_youtube_service(self):
        """Initializes YouTube API v3 client from authorized token file."""
        candidates = [
            self.token_path,
            Path("config/youtube_token.json").resolve(),
            Path("D:/ai-video/youtube_token.json").resolve(),
        ]
        found = next((p for p in candidates if p.exists()), None)
        if not found:
            raise FileNotFoundError(f"YouTube credentials token not found at candidates: {candidates}")

        creds = Credentials.from_authorized_user_file(str(found))
        return build("youtube", "v3", credentials=creds)

    def _parse_duration_seconds(self, iso_duration: str | None) -> float:
        """Parses ISO 8601 duration (e.g. PT58S, PT2M10S, PT1H15M) into float seconds."""
        if not iso_duration:
            return 0.0
        match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso_duration)
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            return float(hours * 3600 + minutes * 60 + seconds)
        return 0.0


    async def ingest_channel(
        self,
        channel_id: str = "UC1ol6l3KL3sgmLPiwQy2QTA",
        include_comments: bool = True,
        max_videos: int | None = None,
    ) -> dict[str, Any]:
        """Performs full extraction of channel, all videos, and all comments."""
        logger.info("Starting complete YouTube Ingestion for Channel ID: %s", channel_id)

        # 1. Fetch Channel Profile & Uploads Playlist
        ch_resp = self.service.channels().list(
            part="snippet,statistics,contentDetails",
            id=channel_id,
        ).execute()

        items = ch_resp.get("items", [])
        if not items:
            raise ValueError(f"Channel not found with ID: {channel_id}")

        ch_data = items[0]
        snippet = ch_data.get("snippet", {})
        stats = ch_data.get("statistics", {})
        content_details = ch_data.get("contentDetails", {})
        uploads_playlist_id = content_details.get("relatedPlaylists", {}).get("uploads")

        channel_profile = {
            "channel_id": channel_id,
            "title": snippet.get("title", ""),
            "custom_url": snippet.get("customUrl"),
            "description": snippet.get("description", ""),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "view_count": int(stats.get("viewCount", 0)),
            "video_count": int(stats.get("videoCount", 0)),
            "uploads_playlist_id": uploads_playlist_id,
            "raw_data": ch_data,
        }
        logger.info("✓ Channel: '%s' | %d Subs | %d Views | %d Videos",
                    channel_profile["title"], channel_profile["subscriber_count"],
                    channel_profile["view_count"], channel_profile["video_count"])

        # 2. Fetch all video IDs from Uploads Playlist
        video_ids: list[str] = []
        next_page_token = None

        logger.info("Extracting all video records from uploads playlist '%s'...", uploads_playlist_id)
        while True:
            pl_resp = self.service.playlistItems().list(
                part="contentDetails",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token,
            ).execute()

            for item in pl_resp.get("items", []):
                v_id = item.get("contentDetails", {}).get("videoId")
                if v_id:
                    video_ids.append(v_id)
                if max_videos and len(video_ids) >= max_videos:
                    break

            next_page_token = pl_resp.get("nextPageToken")
            if not next_page_token or (max_videos and len(video_ids) >= max_videos):
                break

        logger.info("✓ Discovered %d total video IDs on channel", len(video_ids))

        # 3. Batch Fetch Video Details (50 per batch)
        all_videos: list[dict[str, Any]] = []
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i : i + 50]
            v_resp = self.service.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(batch_ids),
            ).execute()

            for v in v_resp.get("items", []):
                v_snip = v.get("snippet", {})
                v_stats = v.get("statistics", {})
                v_content = v.get("contentDetails", {})
                iso_dur = v_content.get("duration")
                dur_secs = self._parse_duration_seconds(iso_dur)

                pub_at_str = v_snip.get("publishedAt")
                pub_at = (
                    datetime.fromisoformat(pub_at_str.replace("Z", "+00:00"))
                    .astimezone(timezone.utc)
                    .replace(tzinfo=None)
                    if pub_at_str
                    else None
                )

                all_videos.append({
                    "video_id": v["id"],
                    "channel_id": channel_id,
                    "title": v_snip.get("title", ""),
                    "description": v_snip.get("description", ""),
                    "published_at": pub_at,
                    "duration": iso_dur,
                    "duration_seconds": dur_secs,
                    "view_count": int(v_stats.get("viewCount", 0)),
                    "like_count": int(v_stats.get("likeCount", 0)),
                    "comment_count": int(v_stats.get("commentCount", 0)),
                    "is_short": dur_secs <= 65.0,  # Shorts are typically <= 60s
                    "tags_json": v_snip.get("tags", []),
                    "raw_data": v,
                })

        logger.info("✓ Extracted metrics for %d videos", len(all_videos))

        # 4. Fetch Comments for all videos with commentCount > 0
        all_comments: list[dict[str, Any]] = []
        if include_comments:
            videos_with_comments = [v for v in all_videos if v["comment_count"] > 0]
            logger.info("Fetching comments for %d videos with comment_count > 0...", len(videos_with_comments))

            for idx, v in enumerate(videos_with_comments, 1):
                v_id = v["video_id"]
                try:
                    c_page_token = None
                    while True:
                        c_resp = self.service.commentThreads().list(
                            part="snippet,replies",
                            videoId=v_id,
                            maxResults=100,
                            textFormat="plainText",
                            pageToken=c_page_token,
                        ).execute()

                        for thread in c_resp.get("items", []):
                            top = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                            top_id = thread.get("snippet", {}).get("topLevelComment", {}).get("id")
                            pub_str = top.get("publishedAt")
                            c_pub = (
                                datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
                                .astimezone(timezone.utc)
                                .replace(tzinfo=None)
                                if pub_str
                                else None
                            )

                            all_comments.append({
                                "comment_id": top_id,
                                "video_id": v_id,
                                "author_name": top.get("authorDisplayName", "Anonymous"),
                                "author_channel_id": top.get("authorChannelId", {}).get("value"),
                                "text": top.get("textDisplay", ""),
                                "like_count": int(top.get("likeCount", 0)),
                                "published_at": c_pub,
                                "parent_id": None,
                                "raw_data": thread,
                            })

                            # Check replies
                            replies = thread.get("replies", {}).get("comments", [])
                            for rep in replies:
                                rep_snip = rep.get("snippet", {})
                                rep_pub_str = rep_snip.get("publishedAt")
                                rep_pub = (
                                    datetime.fromisoformat(rep_pub_str.replace("Z", "+00:00"))
                                    .astimezone(timezone.utc)
                                    .replace(tzinfo=None)
                                    if rep_pub_str
                                    else None
                                )
                                all_comments.append({
                                    "comment_id": rep.get("id"),
                                    "video_id": v_id,
                                    "author_name": rep_snip.get("authorDisplayName", "Anonymous"),
                                    "author_channel_id": rep_snip.get("authorChannelId", {}).get("value"),

                                    "text": rep_snip.get("textDisplay", ""),
                                    "like_count": int(rep_snip.get("likeCount", 0)),
                                    "published_at": rep_pub,
                                    "parent_id": top_id,
                                    "raw_data": rep,
                                })

                        c_page_token = c_resp.get("nextPageToken")
                        if not c_page_token:
                            break
                except HttpError as err:
                    logger.warning("Could not fetch comments for video %s: %s", v_id, err)

            logger.info("✓ Collected %d total viewer comments across channel", len(all_comments))

        # 5. Persist to PostgreSQL Database
        logger.info("Persisting records to PostgreSQL database...")
        async with AsyncSessionLocal() as session:
            # 5.1 Channel Profile Upsert
            stmt_ch = insert(YouTubeChannelRecord).values(
                channel_id=channel_profile["channel_id"],
                title=channel_profile["title"],
                custom_url=channel_profile["custom_url"],
                description=channel_profile["description"],
                subscriber_count=channel_profile["subscriber_count"],
                view_count=channel_profile["view_count"],
                video_count=channel_profile["video_count"],
                uploads_playlist_id=channel_profile["uploads_playlist_id"],
                raw_data=channel_profile["raw_data"],
            ).on_conflict_do_update(
                index_elements=["channel_id"],
                set_={
                    "title": channel_profile["title"],
                    "subscriber_count": channel_profile["subscriber_count"],
                    "view_count": channel_profile["view_count"],
                    "video_count": channel_profile["video_count"],
                    "raw_data": channel_profile["raw_data"],
                }
            )
            await session.execute(stmt_ch)

            # 5.2 Videos Upsert
            for v in all_videos:
                stmt_v = insert(YouTubeVideoRecord).values(
                    video_id=v["video_id"],
                    channel_id=v["channel_id"],
                    title=v["title"],
                    description=v["description"],
                    published_at=v["published_at"],
                    duration=v["duration"],
                    duration_seconds=v["duration_seconds"],
                    view_count=v["view_count"],
                    like_count=v["like_count"],
                    comment_count=v["comment_count"],
                    is_short=v["is_short"],
                    tags_json=v["tags_json"],
                    raw_data=v["raw_data"],
                ).on_conflict_do_update(
                    index_elements=["video_id"],
                    set_={
                        "title": v["title"],
                        "view_count": v["view_count"],
                        "like_count": v["like_count"],
                        "comment_count": v["comment_count"],
                        "raw_data": v["raw_data"],
                    }
                )
                await session.execute(stmt_v)

            # 5.3 Comments Upsert
            for c in all_comments:
                stmt_c = insert(YouTubeCommentRecord).values(
                    comment_id=c["comment_id"],
                    video_id=c["video_id"],
                    author_name=c["author_name"],
                    author_channel_id=c["author_channel_id"],
                    text=c["text"],
                    like_count=c["like_count"],
                    published_at=c["published_at"],
                    parent_id=c["parent_id"],
                    raw_data=c["raw_data"],
                ).on_conflict_do_update(
                    index_elements=["comment_id"],
                    set_={
                        "text": c["text"],
                        "like_count": c["like_count"],
                        "raw_data": c["raw_data"],
                    }
                )
                await session.execute(stmt_c)

            await session.commit()
            logger.info("✓ PostgreSQL sync complete!")

        # 6. Save Local JSON Dump
        dump_file = self.output_dir / "jermina_ai_full_dump.json"
        dump_data = {
            "channel": channel_profile,
            "videos_count": len(all_videos),
            "comments_count": len(all_comments),
            "videos": all_videos,
            "comments": all_comments,
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

        # Serialize datetime objects
        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        dump_file.write_text(json.dumps(dump_data, indent=2, ensure_ascii=False, default=default_serializer), encoding="utf-8")
        logger.info("✓ Full JSON backup saved to: %s", dump_file)

        return {
            "channel": channel_profile["title"],
            "channel_id": channel_id,
            "videos_synced": len(all_videos),
            "comments_synced": len(all_comments),
            "dump_path": str(dump_file),
        }
