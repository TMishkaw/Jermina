"""Sanitized Database Export & Restore Engine for Zero-Leak Git Persistence.

Enables automated, version-controlled persistence of learned agent memories,
motion kinematics, and YouTube analytics in Git while strictly enforcing the
Zero-Leak security policy (api_keys table is strictly blacklisted and omitted).
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import delete, select

from jemini.storage.database import AsyncSessionLocal, init_db
from jemini.storage.models import (
    AgentMemory,
    StickmanMotionRecord,
    YouTubeChannelRecord,
    YouTubeCommentRecord,
    YouTubeVideoRecord,
)

logger = logging.getLogger(__name__)

# Strict blacklist for tables containing credentials or transient logs
BLACKLISTED_TABLES = {"api_keys"}

# Directory for version-controlled sanitized seed backups
DEFAULT_EXPORT_DIR = Path("seeds/sanitized_db")


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder handling datetimes and vector lists."""

    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        if hasattr(o, "tolist"):  # numpy array / pgvector
            return o.tolist()
        return super().default(o)


async def export_sanitized_db(output_dir: Path | str = DEFAULT_EXPORT_DIR) -> dict[str, int]:
    """Exports all non-secret database tables to version-controlled JSON files.

    Returns a dictionary mapping table name to number of exported records.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    summary: dict[str, int] = {}

    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Agent Memories (learned rules, self-evolution feedback, guidelines)
        memories_stmt = select(AgentMemory).order_by(AgentMemory.id)
        memories = (await session.execute(memories_stmt)).scalars().all()
        memories_data = [
            {
                "id": m.id,
                "channel_id": m.channel_id,
                "category": m.category,
                "content": m.content,
                "embedding": list(m.embedding) if m.embedding is not None else None,
                "metadata_json": m.metadata_json or {},
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in memories
        ]
        (out_path / "agent_memories.json").write_text(
            json.dumps(memories_data, indent=2, ensure_ascii=False, cls=DateTimeEncoder),
            encoding="utf-8",
        )
        summary["agent_memories"] = len(memories_data)

        # 2. Stickman Motions (scalable kinematic specs, A/B winners, custom poses)
        motions_stmt = select(StickmanMotionRecord).order_by(StickmanMotionRecord.motion_id)
        motions = (await session.execute(motions_stmt)).scalars().all()
        motions_data = [
            {
                "motion_id": m.motion_id,
                "category": m.category,
                "intent_description": m.intent_description,
                "keywords": m.keywords or [],
                "kinematic_spec": m.kinematic_spec or {},
                "embedding": list(m.embedding) if m.embedding is not None else None,
                "consecutive_wins": m.consecutive_wins,
                "win_rate": m.win_rate,
                "version": m.version,
                "status": m.status,
                "evolution_notes": m.evolution_notes,
                "created_at": m.created_at.isoformat() if m.created_at else None,
                "updated_at": m.updated_at.isoformat() if m.updated_at else None,
            }
            for m in motions
        ]
        (out_path / "stickman_motions.json").write_text(
            json.dumps(motions_data, indent=2, ensure_ascii=False, cls=DateTimeEncoder),
            encoding="utf-8",
        )
        summary["stickman_motions"] = len(motions_data)

        # 3. YouTube Channels
        channels_stmt = select(YouTubeChannelRecord).order_by(YouTubeChannelRecord.channel_id)
        channels = (await session.execute(channels_stmt)).scalars().all()
        channels_data = [
            {
                "channel_id": c.channel_id,
                "title": c.title,
                "custom_url": c.custom_url,
                "description": c.description,
                "subscriber_count": c.subscriber_count,
                "view_count": c.view_count,
                "video_count": c.video_count,
                "uploads_playlist_id": c.uploads_playlist_id,
                "raw_data": c.raw_data or {},
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in channels
        ]
        (out_path / "youtube_channels.json").write_text(
            json.dumps(channels_data, indent=2, ensure_ascii=False, cls=DateTimeEncoder),
            encoding="utf-8",
        )
        summary["youtube_channels"] = len(channels_data)

        # 4. YouTube Videos
        videos_stmt = select(YouTubeVideoRecord).order_by(YouTubeVideoRecord.published_at.desc())
        videos = (await session.execute(videos_stmt)).scalars().all()
        videos_data = [
            {
                "video_id": v.video_id,
                "channel_id": v.channel_id,
                "title": v.title,
                "description": v.description,
                "published_at": v.published_at.isoformat() if v.published_at else None,
                "duration": v.duration,
                "duration_seconds": v.duration_seconds,
                "view_count": v.view_count,
                "like_count": v.like_count,
                "comment_count": v.comment_count,
                "is_short": v.is_short,
                "tags_json": v.tags_json or [],
                "raw_data": v.raw_data or {},
                "updated_at": v.updated_at.isoformat() if v.updated_at else None,
            }
            for v in videos
        ]
        (out_path / "youtube_videos.json").write_text(
            json.dumps(videos_data, indent=2, ensure_ascii=False, cls=DateTimeEncoder),
            encoding="utf-8",
        )
        summary["youtube_videos"] = len(videos_data)

        # 5. YouTube Comments
        comments_stmt = select(YouTubeCommentRecord).order_by(YouTubeCommentRecord.published_at.desc())
        comments = (await session.execute(comments_stmt)).scalars().all()
        comments_data = [
            {
                "comment_id": c.comment_id,
                "video_id": c.video_id,
                "author_name": c.author_name,
                "author_channel_id": c.author_channel_id,
                "text": c.text,
                "like_count": c.like_count,
                "published_at": c.published_at.isoformat() if c.published_at else None,
                "parent_id": c.parent_id,
                "sentiment": c.sentiment,
                "audience_topic": c.audience_topic,
                "analyzed_at": c.analyzed_at.isoformat() if c.analyzed_at else None,
                "raw_data": c.raw_data or {},
            }
            for c in comments
        ]
        (out_path / "youtube_comments.json").write_text(
            json.dumps(comments_data, indent=2, ensure_ascii=False, cls=DateTimeEncoder),
            encoding="utf-8",
        )
        summary["youtube_comments"] = len(comments_data)

    logger.info("✓ Sanitized database exported to %s: %s", out_path, summary)
    return summary


async def restore_sanitized_db(
    input_dir: Path | str = DEFAULT_EXPORT_DIR,
    clear_existing: bool = False,
) -> dict[str, int]:
    """Restores database tables from version-controlled JSON export files.

    Performs upsert operations preserving newly acquired data.
    """
    in_path = Path(input_dir)
    if not in_path.exists():
        logger.warning("Sanitized DB input directory %s does not exist, skipping restore.", in_path)
        return {}

    summary: dict[str, int] = {}
    await init_db()

    async with AsyncSessionLocal() as session:
        # 1. Restore Stickman Motions
        motions_file = in_path / "stickman_motions.json"
        if motions_file.exists():
            if clear_existing:
                await session.execute(delete(StickmanMotionRecord))
            motions_raw = json.loads(motions_file.read_text(encoding="utf-8"))
            count = 0
            for item in motions_raw:
                stmt = select(StickmanMotionRecord).where(StickmanMotionRecord.motion_id == item["motion_id"])
                rec = (await session.execute(stmt)).scalars().first()
                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                created = datetime.fromisoformat(item["created_at"]) if item.get("created_at") else now_utc
                updated = datetime.fromisoformat(item["updated_at"]) if item.get("updated_at") else now_utc

                if not rec:
                    rec = StickmanMotionRecord(
                        motion_id=item["motion_id"],
                        category=item.get("category", "general"),
                        intent_description=item.get("intent_description", ""),
                        keywords=item.get("keywords", []),
                        kinematic_spec=item.get("kinematic_spec", {}),
                        embedding=item.get("embedding"),
                        consecutive_wins=item.get("consecutive_wins", 2),
                        win_rate=item.get("win_rate", 1.0),
                        version=item.get("version", "v1.0"),
                        status=item.get("status", "active"),
                        evolution_notes=item.get("evolution_notes"),
                        created_at=created,
                        updated_at=updated,
                    )
                    session.add(rec)
                else:
                    rec.category = item.get("category", rec.category)
                    rec.intent_description = item.get("intent_description", rec.intent_description)
                    rec.keywords = item.get("keywords", rec.keywords)
                    rec.kinematic_spec = item.get("kinematic_spec", rec.kinematic_spec)
                    rec.embedding = item.get("embedding", rec.embedding)
                    rec.evolution_notes = item.get("evolution_notes", rec.evolution_notes)
                    rec.updated_at = updated
                count += 1
            await session.commit()
            summary["stickman_motions"] = count

        # 2. Restore Agent Memories
        memories_file = in_path / "agent_memories.json"
        if memories_file.exists():
            if clear_existing:
                await session.execute(delete(AgentMemory))
            memories_raw = json.loads(memories_file.read_text(encoding="utf-8"))
            count = 0
            for item in memories_raw:
                mem_id = item.get("id")
                rec = None
                if mem_id is not None:
                    stmt = select(AgentMemory).where(AgentMemory.id == mem_id)
                    rec = (await session.execute(stmt)).scalars().first()

                now_utc = datetime.now(timezone.utc).replace(tzinfo=None)
                created = datetime.fromisoformat(item["created_at"]) if item.get("created_at") else now_utc
                if not rec:
                    rec = AgentMemory(
                        id=mem_id,
                        channel_id=item["channel_id"],
                        category=item.get("category", "context"),
                        content=item["content"],
                        embedding=item.get("embedding"),
                        metadata_json=item.get("metadata_json", {}),
                        created_at=created,
                    )
                    session.add(rec)
                else:
                    rec.category = item.get("category", rec.category)
                    rec.content = item["content"]
                    rec.embedding = item.get("embedding", rec.embedding)
                    rec.metadata_json = item.get("metadata_json", rec.metadata_json)
                count += 1
            await session.commit()
            summary["agent_memories"] = count

        # 3. Restore YouTube Channels
        channels_file = in_path / "youtube_channels.json"
        if channels_file.exists():
            channels_raw = json.loads(channels_file.read_text(encoding="utf-8"))
            count = 0
            for item in channels_raw:
                stmt = select(YouTubeChannelRecord).where(YouTubeChannelRecord.channel_id == item["channel_id"])
                rec = (await session.execute(stmt)).scalars().first()
                if not rec:
                    rec = YouTubeChannelRecord(
                        channel_id=item["channel_id"],
                        title=item.get("title", ""),
                        custom_url=item.get("custom_url"),
                        description=item.get("description", ""),
                        subscriber_count=item.get("subscriber_count", 0),
                        view_count=item.get("view_count", 0),
                        video_count=item.get("video_count", 0),
                        uploads_playlist_id=item.get("uploads_playlist_id"),
                        raw_data=item.get("raw_data", {}),
                    )
                    session.add(rec)
                count += 1
            await session.commit()
            summary["youtube_channels"] = count

        # 4. Restore YouTube Videos
        videos_file = in_path / "youtube_videos.json"
        if videos_file.exists():
            videos_raw = json.loads(videos_file.read_text(encoding="utf-8"))
            count = 0
            for item in videos_raw:
                stmt = select(YouTubeVideoRecord).where(YouTubeVideoRecord.video_id == item["video_id"])
                rec = (await session.execute(stmt)).scalars().first()
                pub_at = datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None
                if not rec:
                    rec = YouTubeVideoRecord(
                        video_id=item["video_id"],
                        channel_id=item.get("channel_id", "default"),
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        published_at=pub_at,
                        duration=item.get("duration"),
                        duration_seconds=item.get("duration_seconds", 0.0),
                        view_count=item.get("view_count", 0),
                        like_count=item.get("like_count", 0),
                        comment_count=item.get("comment_count", 0),
                        is_short=item.get("is_short", True),
                        tags_json=item.get("tags_json", []),
                        raw_data=item.get("raw_data", {}),
                    )
                    session.add(rec)
                count += 1
            await session.commit()
            summary["youtube_videos"] = count

        # 5. Restore YouTube Comments
        comments_file = in_path / "youtube_comments.json"
        if comments_file.exists():
            comments_raw = json.loads(comments_file.read_text(encoding="utf-8"))
            count = 0
            for item in comments_raw:
                stmt = select(YouTubeCommentRecord).where(YouTubeCommentRecord.comment_id == item["comment_id"])
                rec = (await session.execute(stmt)).scalars().first()
                pub_at = datetime.fromisoformat(item["published_at"]) if item.get("published_at") else None
                ana_at = datetime.fromisoformat(item["analyzed_at"]) if item.get("analyzed_at") else None
                if not rec:
                    rec = YouTubeCommentRecord(
                        comment_id=item["comment_id"],
                        video_id=item.get("video_id", ""),
                        author_name=item.get("author_name", ""),
                        author_channel_id=item.get("author_channel_id"),
                        text=item.get("text", ""),
                        like_count=item.get("like_count", 0),
                        published_at=pub_at,
                        parent_id=item.get("parent_id"),
                        sentiment=item.get("sentiment"),
                        audience_topic=item.get("audience_topic"),
                        analyzed_at=ana_at,
                        raw_data=item.get("raw_data", {}),
                    )
                    session.add(rec)
                count += 1
            await session.commit()
            summary["youtube_comments"] = count

    logger.info("✓ Sanitized database restored from %s: %s", in_path, summary)
    return summary
