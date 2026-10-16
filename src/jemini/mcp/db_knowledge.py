"""Dynamic Database Knowledge Navigator for Jemini Studio MCP.

Provides structured, real-time querying of long-term agent memories,
stickman kinematic presets, YouTube channel metrics, and audience feedback.
Includes graceful fallback to seeds/sanitized_db/*.json if PostgreSQL is offline.
"""

from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import text

logger = logging.getLogger(__name__)


class DBKnowledgeEngine:
    """Queries live PostgreSQL database knowledge with offline JSON fallback."""

    def __init__(self, seeds_dir: Path | str = "seeds/sanitized_db"):
        self.seeds_dir = Path(seeds_dir).resolve()

    def _read_seed_file(self, filename: str) -> list[dict[str, Any]]:
        """Reads sanitized JSON seed as a fallback."""
        file_path = self.seeds_dir / filename
        if file_path.exists():
            try:
                return json.loads(file_path.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Error reading seed file %s: %s", file_path, exc)
        return []

    async def query_memories(
        self,
        category: str | None = None,
        query: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Queries agent memories from PostgreSQL or sanitized fallback."""
        limit = min(max(1, limit), 50)
        try:
            from jemini.storage.database import engine

            async with engine.begin() as conn:
                clauses = []
                params: dict[str, Any] = {"lim": limit}
                if category:
                    clauses.append("category = :cat")
                    params["cat"] = category
                if query:
                    clauses.append("content ILIKE :q")
                    params["q"] = f"%{query}%"

                where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
                sql_str = f"SELECT id, channel_id, category, content, metadata_json, created_at FROM agent_memories {where_sql} ORDER BY id DESC LIMIT :lim"
                res = await conn.execute(text(sql_str), params)
                rows = res.fetchall()
                if rows:
                    return [
                        {
                            "id": r[0],
                            "channel_id": r[1],
                            "category": r[2],
                            "content": r[3],
                            "metadata": r[4],
                            "created_at": str(r[5]),
                        }
                        for r in rows
                    ]
        except Exception as exc:  # noqa: BLE001
            logger.info("Live DB query failed (%s), using sanitized seeds.", exc)

        # Fallback to seeds/sanitized_db/agent_memories.json
        items = self._read_seed_file("agent_memories.json")
        filtered = []
        q_lower = query.lower() if query else None
        cat_lower = category.lower() if category else None

        for item in items:
            if cat_lower and item.get("category", "").lower() != cat_lower:
                continue
            if q_lower and q_lower not in item.get("content", "").lower():
                continue
            filtered.append(item)
            if len(filtered) >= limit:
                break
        return filtered

    async def query_motions(
        self,
        category: str | None = None,
        query: str | None = None,
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        """Queries stickman motions and kinematics from PostgreSQL or fallback."""
        limit = min(max(1, limit), 50)
        try:
            from jemini.storage.database import engine

            async with engine.begin() as conn:
                clauses = []
                params: dict[str, Any] = {"lim": limit}
                if category:
                    clauses.append("category = :cat")
                    params["cat"] = category
                if query:
                    clauses.append("(motion_id ILIKE :q OR intent_description ILIKE :q)")
                    params["q"] = f"%{query}%"

                where_sql = ("WHERE " + " AND ".join(clauses)) if clauses else ""
                sql_str = f"SELECT motion_id, category, intent_description, kinematic_spec, consecutive_wins, win_rate, status FROM stickman_motions {where_sql} ORDER BY motion_id ASC LIMIT :lim"
                res = await conn.execute(text(sql_str), params)
                rows = res.fetchall()
                if rows:
                    return [
                        {
                            "motion_id": r[0],
                            "category": r[1],
                            "intent_description": r[2],
                            "kinematic_spec": r[3],
                            "consecutive_wins": r[4],
                            "win_rate": r[5],
                            "status": r[6],
                        }
                        for r in rows
                    ]
        except Exception as exc:  # noqa: BLE001
            logger.info("Live DB motions query failed (%s), using sanitized seeds.", exc)

        items = self._read_seed_file("stickman_motions.json")
        filtered = []
        q_lower = query.lower() if query else None
        cat_lower = category.lower() if category else None

        for item in items:
            if cat_lower and item.get("category", "").lower() != cat_lower:
                continue
            if q_lower and (
                q_lower not in item.get("motion_id", "").lower()
                and q_lower not in item.get("intent_description", "").lower()
            ):
                continue
            filtered.append(item)
            if len(filtered) >= limit:
                break
        return filtered

    async def query_channel_and_videos(
        self,
        sort_by: str = "view_count",
        query: str | None = None,
        limit: int = 5,
    ) -> dict[str, Any]:
        """Queries channel summary and top videos."""
        limit = min(max(1, limit), 20)
        channel_data: dict[str, Any] = {}
        videos_data: list[dict[str, Any]] = []

        try:
            from jemini.storage.database import engine

            async with engine.begin() as conn:
                ch_res = await conn.execute(text("SELECT channel_id, title, subscriber_count, view_count, video_count FROM youtube_channels LIMIT 1"))
                ch_row = ch_res.fetchone()
                if ch_row:
                    channel_data = {
                        "channel_id": ch_row[0],
                        "title": ch_row[1],
                        "subscriber_count": ch_row[2],
                        "view_count": ch_row[3],
                        "video_count": ch_row[4],
                    }

                order_col = "view_count" if sort_by not in ("like_count", "comment_count") else sort_by
                q_clause = "WHERE title ILIKE :q" if query else ""
                sql_v = f"SELECT video_id, title, view_count, like_count, comment_count, is_short, tags_json FROM youtube_videos {q_clause} ORDER BY {order_col} DESC LIMIT :lim"
                params: dict[str, Any] = {"lim": limit}
                if query:
                    params["q"] = f"%{query}%"

                v_res = await conn.execute(text(sql_v), params)
                for r in v_res.fetchall():
                    videos_data.append({
                        "video_id": r[0],
                        "title": r[1],
                        "view_count": r[2],
                        "like_count": r[3],
                        "comment_count": r[4],
                        "is_short": r[5],
                        "tags": r[6],
                    })
        except Exception as exc:  # noqa: BLE001
            logger.info("Live DB channel/videos query failed (%s), using sanitized seeds.", exc)

        if not channel_data:
            chs = self._read_seed_file("youtube_channels.json")
            if chs:
                channel_data = chs[0]

        if not videos_data:
            vids = self._read_seed_file("youtube_videos.json")
            q_lower = query.lower() if query else None
            matched = [v for v in vids if (not q_lower or q_lower in v.get("title", "").lower())]
            sort_key = sort_by if sort_by in ("view_count", "like_count", "comment_count") else "view_count"
            sorted_vids = sorted(matched, key=lambda x: x.get(sort_key, 0), reverse=True)
            videos_data = sorted_vids[:limit]

        return {"channel": channel_data, "videos": videos_data}

    async def execute_query(
        self,
        topic: str,
        query: str | None = None,
        category: str | None = None,
        limit: int = 10,
    ) -> str:
        """Executes knowledge lookup and returns formatted Markdown text."""
        topic_clean = topic.lower().strip()

        if topic_clean in ("memories", "memory", "agent_memories"):
            records = await self.query_memories(category=category, query=query, limit=limit)
            if not records:
                return f"No memories found matching query '{query}' (category: '{category}')."
            lines = [f"# Agent Memories Knowledge ({len(records)} entries):\n"]
            for r in records:
                cid = r.get("category", "general")
                created = r.get("created_at", "")[:19]
                lines.append(f"### [{cid}] ID #{r.get('id', 'N/A')} ({created})")
                lines.append(f"{r.get('content', '')}\n")
            return "\n".join(lines)

        if topic_clean in ("motions", "stickman", "gestures"):
            motions = await self.query_motions(category=category, query=query, limit=limit)
            if not motions:
                return f"No stickman motions found matching query '{query}'."
            lines = [f"# Stickman Motions Knowledge ({len(motions)} presets):\n"]
            lines.append("| Motion ID | Category | Consecutive Wins | Description |")
            lines.append("| :--- | :--- | :---: | :--- |")
            for m in motions:
                lines.append(f"| `{m['motion_id']}` | {m.get('category')} | {m.get('consecutive_wins', 2)} | {m.get('intent_description')} |")
            return "\n".join(lines)

        if topic_clean in ("channel", "videos", "youtube_videos"):
            data = await self.query_channel_and_videos(query=query, limit=limit)
            ch = data.get("channel", {})
            vids = data.get("videos", [])
            lines = [
                f"# YouTube Channel Performance Knowledge: {ch.get('title', 'Jermina')}\n",
                f"- **Subscribers:** {ch.get('subscriber_count', 0):,}",
                f"- **Total Views:** {ch.get('view_count', 0):,}",
                f"- **Total Videos:** {ch.get('video_count', 0):,}\n",
                "## Top Performing Videos:\n",
                "| Video Title | Views | Likes | Comments |",
                "| :--- | :---: | :---: | :---: |",
            ]
            for v in vids:
                lines.append(f"| {v.get('title', '')[:60]} | {v.get('view_count', 0):,} | {v.get('like_count', 0):,} | {v.get('comment_count', 0):,} |")
            return "\n".join(lines)

        return f"Unknown DB knowledge topic '{topic}'. Supported: 'memories', 'motions', 'videos', 'channel'."


def query_db_knowledge_sync(
    topic: str,
    query: str | None = None,
    category: str | None = None,
    limit: int = 10,
) -> str:
    """Synchronous bridge for query execution in stdio server."""
    engine = DBKnowledgeEngine()
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, engine.execute_query(topic=topic, query=query, category=category, limit=limit)).result()
    else:
        return loop.run_until_complete(engine.execute_query(topic=topic, query=query, category=category, limit=limit))
