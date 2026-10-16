"""Database models for PostgreSQL and pgvector long-term agent memory."""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, DateTime, Float, Integer, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase):
    pass

class AgentMemory(Base):
    """Long-term associative memory for Jemini agents using pgvector embeddings."""
    __tablename__ = "agent_memories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    category: Mapped[str] = mapped_column(String(64), index=True)  # e.g. "script_pattern", "failure_case"
    content: Mapped[str] = mapped_column(Text)
    # 768-dim or 1536-dim vector for Gemini embeddings
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768), nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ChannelAuditLog(Base):
    """Immutable execution log for all channel operations and publication attempts."""
    __tablename__ = "channel_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    channel_id: Mapped[str] = mapped_column(String(64), index=True)
    action: Mapped[str] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32))  # success, failure, retry
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
