"""Unit tests for DBKnowledgeEngine (PostgreSQL with sanitized fallback)."""

import pytest

from jemini.mcp.db_knowledge import DBKnowledgeEngine


@pytest.fixture
def db_engine():
    return DBKnowledgeEngine()


@pytest.mark.asyncio
async def test_db_knowledge_memories(db_engine):
    memories = await db_engine.query_memories(category="context", limit=5)
    assert len(memories) > 0
    assert any("Gemini" in m.get("content", "") or "API" in m.get("content", "") for m in memories)


@pytest.mark.asyncio
async def test_db_knowledge_motions(db_engine):
    motions = await db_engine.query_motions(query="stop", limit=5)
    assert len(motions) > 0
    motion_ids = [m.get("motion_id") for m in motions]
    assert any("stop" in mid for mid in motion_ids)


@pytest.mark.asyncio
async def test_db_knowledge_channel_and_videos(db_engine):
    data = await db_engine.query_channel_and_videos(limit=5)
    assert "channel" in data
    assert "videos" in data
    assert len(data["videos"]) > 0


@pytest.mark.asyncio
async def test_db_knowledge_execute_query(db_engine):
    md_memories = await db_engine.execute_query(topic="memories", limit=3)
    assert "# Agent Memories Knowledge" in md_memories

    md_motions = await db_engine.execute_query(topic="motions", limit=3)
    assert "# Stickman Motions Knowledge" in md_motions

    md_videos = await db_engine.execute_query(topic="videos", limit=3)
    assert "# YouTube Channel Performance Knowledge" in md_videos
