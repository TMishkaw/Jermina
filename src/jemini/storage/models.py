"""Database models for PostgreSQL and pgvector with Key Management and Memory."""

from datetime import datetime
from enum import Enum
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class KeyType(str, Enum):
    FREE = "free"
    PAID = "paid"

class KeyStatus(str, Enum):
    ACTIVE = "active"
    RATE_LIMITED = "rate_limited"
    EXHAUSTED = "exhausted"
    BANNED = "banned"

class APIKeyRecord(Base):
    """Centralized API Key entity with per-model quota tracking and free-tier priority."""
    __tablename__ = "api_keys"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    key_string: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    engine: Mapped[str] = mapped_column(String(64), default="gemini", index=True)  # gemini, openai, etc.
    key_type: Mapped[str] = mapped_column(String(32), default=KeyType.FREE.value, index=True)  # free, paid
    status: Mapped[str] = mapped_column(String(32), default=KeyStatus.ACTIVE.value, index=True)
    
    # Per-model cooldowns: {"gemini-2.5-flash": 1729080000.0, "gemini-3.8-live": 1729081200.0}
    cooldowns_json: Mapped[dict[str, float]] = mapped_column(JSON, default=dict)
    
    # Models mapping and quota constraints: {"gemini-2.5-flash": {"rpm": 15, "rpd": 1500}}
    models_mapping: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    
    total_requests: Mapped[int] = mapped_column(Integer, default=0)
    failed_requests: Mapped[int] = mapped_column(Integer, default=0)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentMemoryCategory(str, Enum):
    CONTEXT = "context"
    EXPERIMENT_EXPERIENCE = "experiment_experience"
    PARSING_ERROR = "parsing_error"
    SCRIPT_PATTERN = "script_pattern"

class AgentMemory(Base):
    """Long-term associative memory for Jemini agents using pgvector embeddings."""
    __tablename__ = "agent_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # context, experiment_experience, parsing_error, script_pattern
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class LiveStreamEventRecord(Base):
    """Events parsed visually or via streams during live broadcasts (TikTok / YouTube)."""
    __tablename__ = "live_stream_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    platform: Mapped[str] = mapped_column(String(32), index=True)  # tiktok, youtube
    event_type: Mapped[str] = mapped_column(String(64), index=True)  # gift, comment, like, action, chat_event
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ChannelAuditLog(Base):
    """Structured immutable audit and execution logs in PostgreSQL."""
    __tablename__ = "channel_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))  # success, failure, retry, graceful_degradation
    details: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class YouTubeChannelRecord(Base):
    """YouTube channel profile and global performance statistics."""
    __tablename__ = "youtube_channels"

    channel_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    custom_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    subscriber_count: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    video_count: Mapped[int] = mapped_column(Integer, default=0)
    uploads_playlist_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class YouTubeVideoRecord(Base):
    """Archived YouTube videos with metadata, views, likes, and comment metrics."""
    __tablename__ = "youtube_videos"

    video_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration: Mapped[str | None] = mapped_column(String(64), nullable=True)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    is_short: Mapped[bool] = mapped_column(default=True)
    tags_json: Mapped[list[str]] = mapped_column(JSON, default=list)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class YouTubeCommentRecord(Base):
    """Viewer comments and replies for sentiment and topic mining."""
    __tablename__ = "youtube_comments"

    comment_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    video_id: Mapped[str] = mapped_column(String(64), index=True)
    author_name: Mapped[str] = mapped_column(String(255))
    author_channel_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    text: Mapped[str] = mapped_column(Text)
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    sentiment: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    audience_topic: Mapped[str | None] = mapped_column(Text, nullable=True)
    analyzed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    raw_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)


class StickmanMotionRecord(Base):
    """Scalable dynamic motion library storing kinematic parameters, props, and vector embeddings."""
    __tablename__ = "stickman_motions"

    motion_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # emotion, gesture, prop, reaction, action
    intent_description: Mapped[str] = mapped_column(Text)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list)  # Ukrainian keywords & synonyms
    kinematic_spec: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)  # angles, timing, bounce, prop, emoji
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    consecutive_wins: Mapped[int] = mapped_column(Integer, default=2)
    win_rate: Mapped[float] = mapped_column(Float, default=1.0)
    version: Mapped[str] = mapped_column(String(16), default="v1.0")
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    evolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


