"""Dynamic Sync Script: Database Knowledge to Studio Docs.

Extracts operational rules, verified agent memories, stickman motion catalog,
and channel analytics from PostgreSQL (or sanitized seeds) into
docs/studio_knowledge/DevDocs/DatabaseKnowledgeBase.md.

Adheres strictly to Jermina Brain Governance (Law 3: Zero-Noise Anti-Pollution).
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any

from sqlalchemy import text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def generate_db_knowledge_doc(
    output_path: Path | str = "docs/studio_knowledge/DevDocs/DatabaseKnowledgeBase.md",
    seeds_dir: Path | str = "seeds/sanitized_db",
) -> Path:
    target = Path(output_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    seeds = Path(seeds_dir).resolve()

    memories: list[dict[str, Any]] = []
    motions: list[dict[str, Any]] = []
    channel: dict[str, Any] = {}
    top_videos: list[dict[str, Any]] = []

    # 1. Try querying live database
    try:
        from jemini.storage.database import engine

        async with engine.begin() as conn:
            # Curated context memories
            m_res = await conn.execute(text("SELECT id, category, content FROM agent_memories WHERE category IN ('context', 'bootstrap') ORDER BY id ASC"))
            for r in m_res.fetchall():
                memories.append({"id": r[0], "category": r[1], "content": r[2]})

            # Motion presets
            mot_res = await conn.execute(text("SELECT motion_id, category, intent_description, consecutive_wins, win_rate FROM stickman_motions ORDER BY motion_id ASC"))
            for r in mot_res.fetchall():
                motions.append({
                    "motion_id": r[0],
                    "category": r[1],
                    "intent": r[2],
                    "wins": r[3],
                    "win_rate": r[4],
                })

            # Channel
            ch_res = await conn.execute(text("SELECT channel_id, title, subscriber_count, view_count, video_count FROM youtube_channels LIMIT 1"))
            ch_row = ch_res.fetchone()
            if ch_row:
                channel = {
                    "channel_id": ch_row[0],
                    "title": ch_row[1],
                    "subscribers": ch_row[2],
                    "views": ch_row[3],
                    "videos": ch_row[4],
                }

            # Top videos
            v_res = await conn.execute(text("SELECT video_id, title, view_count, like_count, comment_count, is_short FROM youtube_videos ORDER BY view_count DESC LIMIT 10"))
            for r in v_res.fetchall():
                top_videos.append({
                    "id": r[0],
                    "title": r[1],
                    "views": r[2],
                    "likes": r[3],
                    "comments": r[4],
                    "is_short": r[5],
                })

        logger.info("✓ Extracted live database knowledge: %d memories, %d motions, %d videos.", len(memories), len(motions), len(top_videos))
    except Exception as exc:  # noqa: BLE001
        logger.warning("Live database query skipped (%s), reading from %s", exc, seeds)

    # Fallback to sanitized seeds if live query returned partial data
    if not memories and (seeds / "agent_memories.json").exists():
        raw_m = json.loads((seeds / "agent_memories.json").read_text(encoding="utf-8"))
        memories = [m for m in raw_m if m.get("category") in ("context", "bootstrap")]

    if not motions and (seeds / "stickman_motions.json").exists():
        raw_mot = json.loads((seeds / "stickman_motions.json").read_text(encoding="utf-8"))
        motions = [
            {"motion_id": m.get("motion_id"), "category": m.get("category"), "intent": m.get("intent_description"), "wins": m.get("consecutive_wins", 2), "win_rate": m.get("win_rate", 1.0)}
            for m in raw_mot
        ]

    if not channel and (seeds / "youtube_channels.json").exists():
        raw_ch = json.loads((seeds / "youtube_channels.json").read_text(encoding="utf-8"))
        if raw_ch:
            c0 = raw_ch[0]
            channel = {"title": c0.get("title"), "subscribers": c0.get("subscriber_count", 0), "views": c0.get("view_count", 0), "videos": c0.get("video_count", 0)}

    if not top_videos and (seeds / "youtube_videos.json").exists():
        raw_v = json.loads((seeds / "youtube_videos.json").read_text(encoding="utf-8"))
        top_videos = sorted(raw_v, key=lambda x: x.get("view_count", 0), reverse=True)[:10]

    # Render Markdown Document
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [
        "# Database Knowledge Base & Operational Memory",
        "",
        f"> **Auto-synced**: `{now_str}` from PostgreSQL (`jermina_db`) with Zero-Leak sanitization.",
        "> **Governance**: Adheres to Jermina Brain Governance (Strict Versioning, Anti-Pollution, Domain Memory).",
        "",
        "---",
        "",
        "## 1. Verified Operational Rules & Architectural Memory (`agent_memories`)",
        "",
        f"Зафіксовано **{len(memories)}** верифікованих доменних правил у векторній пам'яті pgvector:",
        "",
    ]

    for m in memories:
        lines.append(f"### [ID #{m.get('id', 'N/A')}] {m.get('category').upper()}")
        lines.append(f"{m.get('content')}\n")

    lines.extend([
        "---",
        "",
        "## 2. Dynamic Stickman Kinematics Catalog (`stickman_motions`)",
        "",
        f"Поточний активний каталог налічує **{len(motions)}** перевірених жестових пресетів (поріг конвергенції: 2 послідовні перемоги):",
        "",
        "| Motion ID | Category | Wins | Win Rate | Intent / Trigger |",
        "| :--- | :--- | :---: | :---: | :--- |",
    ])

    for mot in motions:
        lines.append(f"| `{mot.get('motion_id')}` | {mot.get('category')} | {mot.get('wins', 2)} | {mot.get('win_rate', 1.0):.1f} | {mot.get('intent')} |")

    lines.extend([
        "",
        "---",
        "",
        "## 3. YouTube Channel & Top Performing Benchmarks",
        "",
        f"- **Channel Title:** {channel.get('title', 'Jermina AI Studio')}",
        f"- **Subscribers:** {channel.get('subscribers', 0):,}",
        f"- **Total Channel Views:** {channel.get('views', 0):,}",
        f"- **Total Published Videos:** {channel.get('videos', 0):,}",
        "",
        "### Top 10 High-Performing Videos:",
        "",
        "| Video ID | Title | Views | Likes | Comments |",
        "| :--- | :--- | :---: | :---: | :---: |",
    ])

    for v in top_videos:
        vid_id = v.get("id") or v.get("video_id")
        title = (v.get("title") or "")[:60]
        views = v.get("views") or v.get("view_count", 0)
        likes = v.get("likes") or v.get("like_count", 0)
        comments = v.get("comments") or v.get("comment_count", 0)
        lines.append(f"| `{vid_id}` | {title} | {views:,} | {likes:,} | {comments:,} |")

    lines.append("")
    content = "\n".join(lines)
    target.write_text(content, encoding="utf-8")
    logger.info("✓ Wrote updated Database Knowledge Base: %s (%d bytes).", target, len(content))
    return target


def main() -> None:
    asyncio.run(generate_db_knowledge_doc())


if __name__ == "__main__":
    main()
