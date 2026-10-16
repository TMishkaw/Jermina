"""Scalable Dynamic Motion Library & Evolution Engine for Stickman Animations.

Manages persistent storage, vector search, and autonomous self-evolution for an
expanding repository of thousands of kinematic stickman movements, gestures, and props.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from google import genai
from sqlalchemy import select, text

from jemini.core.config import settings
from jemini.rotator.rotator import APIKeyRotator
from jemini.rotator.router import TaskTier
from jemini.storage.database import AsyncSessionLocal, engine
from jemini.storage.models import Base, StickmanMotionRecord
from jemini.validation.ab_testing import ABTestConvergenceResult

logger = logging.getLogger(__name__)


@dataclass
class MotionSpec:
    """In-memory representation of a single kinematic movement preset."""
    motion_id: str
    category: str
    intent_description: str
    keywords: list[str]
    animation: str
    eye_type: str
    mouth_type: str
    prop: str
    emoji: str | None
    custom_pose: dict[str, Any] | None = None
    version: str = "v1.0"
    status: str = "active"


class MotionLibraryManager:
    """Orchestrates persistent storage, pgvector retrieval, and growth of the motion database."""

    def __init__(
        self,
        rotator: APIKeyRotator | None = None,
        cache_path: Path | str = "data/motions/motion_catalog.json",
        remotion_public_cache: Path | str = "remotion/public/motions/motion_catalog.json",
    ):
        self.rotator = rotator
        self.cache_path = Path(cache_path)
        self.remotion_public_cache = Path(remotion_public_cache)
        self._memory_cache: dict[str, MotionSpec] = {}
        self._ensure_cache_dirs()

    def _ensure_cache_dirs(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.remotion_public_cache.parent.mkdir(parents=True, exist_ok=True)

    async def init_tables(self) -> None:
        """Ensures the stickman_motions table exists in PostgreSQL."""
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("✓ PostgreSQL stickman_motions table verified.")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not initialize PostgreSQL tables: %s", exc)

    async def get_embedding(self, text_input: str) -> list[float] | None:
        """Computes 768-dim text embedding via gemini-embedding-2."""
        if not settings.gemini_api_keys:
            return None

        api_key = settings.gemini_api_keys[0]
        if self.rotator:
            try:
                acquired = await self.rotator.get_active_key(tier=TaskTier.EMBEDDING)
                api_key = acquired.key_string
            except Exception as exc:  # noqa: BLE001
                logger.warning("Key rotator error for embedding, falling back: %s", exc)

        try:
            client = genai.Client(api_key=api_key)
            resp = client.models.embed_content(
                model="gemini-embedding-2",
                contents=text_input,
            )
            if resp.embedding and resp.embedding.values:
                return list(resp.embedding.values)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Embedding generation error (%s)", exc)
        return None

    async def seed_core_ontology(self, ontology_rules: list[Any]) -> int:
        """Seeds the database and local cache from the core semantic ontology."""
        await self.init_tables()
        count = 0
        async with AsyncSessionLocal() as session:
            for keywords, anim, eye, mouth, prop, emojis in ontology_rules:
                motion_id = f"{anim}_{prop}" if prop != "none" else anim
                stmt = select(StickmanMotionRecord).where(StickmanMotionRecord.motion_id == motion_id)
                existing = (await session.execute(stmt)).scalar_one_or_none()

                primary_emoji = emojis[0] if emojis else None
                intent = f"Жест {anim} з реквізитом {prop} для теми: {', '.join(keywords[:3])}"

                kinematics = {
                    "animation": anim,
                    "eye_type": eye,
                    "mouth_type": mouth,
                    "prop": prop,
                    "emoji": primary_emoji,
                    "emojis_pool": emojis,
                }

                if not existing:
                    rec = StickmanMotionRecord(
                        motion_id=motion_id,
                        category="core_gesture",
                        intent_description=intent,
                        keywords=keywords,
                        kinematic_spec=kinematics,
                        version="v1.0",
                        status="active",
                    )
                    session.add(rec)
                    count += 1

                # Update local cache
                self._memory_cache[motion_id] = MotionSpec(
                    motion_id=motion_id,
                    category="core_gesture",
                    intent_description=intent,
                    keywords=keywords,
                    animation=anim,
                    eye_type=eye,
                    mouth_type=mouth,
                    prop=prop,
                    emoji=primary_emoji,
                )

            await session.commit()

        self._flush_cache_to_disk()
        total_seeded = len(self._memory_cache)
        logger.info("✓ Motion Library seeded: %d new inserted to DB. Total active catalog: %d.", count, total_seeded)
        return total_seeded

    async def register_ab_winner(self, convergence_res: ABTestConvergenceResult) -> MotionSpec:
        """Registers or evolves a motion preset based on A/B convergence test results."""
        motion_id = f"{convergence_res.element_name}_evolved"
        intent = convergence_res.intent_description
        spec_data = convergence_res.winning_spec

        anim = spec_data.get("animation", convergence_res.element_name)
        eye = spec_data.get("eye_type", "neutral")
        mouth = spec_data.get("mouth_type", "smile")
        prop = spec_data.get("prop", "none")
        emoji = spec_data.get("emoji", "✨")

        motion = MotionSpec(
            motion_id=motion_id,
            category="evolved_gesture",
            intent_description=intent,
            keywords=[convergence_res.element_name, intent.lower()],
            animation=anim,
            eye_type=eye,
            mouth_type=mouth,
            prop=prop,
            emoji=emoji,
            custom_pose=spec_data.get("custom_pose"),
            version="v2.0",
            status="active",
        )

        # 1. Update in-memory cache
        self._memory_cache[motion_id] = motion
        self._flush_cache_to_disk()

        # 2. Persist to PostgreSQL with pgvector embedding
        emb = await self.get_embedding(f"{intent} {convergence_res.element_name}")
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(StickmanMotionRecord).where(StickmanMotionRecord.motion_id == motion_id)
                rec = (await session.execute(stmt)).scalar_one_or_none()

                if not rec:
                    rec = StickmanMotionRecord(
                        motion_id=motion_id,
                        category="evolved_gesture",
                        intent_description=intent,
                        keywords=motion.keywords,
                        kinematic_spec=spec_data,
                        embedding=emb,
                        consecutive_wins=convergence_res.consecutive_wins,
                        evolution_notes=convergence_res.evolution_direction,
                        version="v2.0",
                    )
                    session.add(rec)
                else:
                    rec.kinematic_spec = spec_data
                    rec.evolution_notes = convergence_res.evolution_direction
                    rec.consecutive_wins = convergence_res.consecutive_wins
                    if emb:
                        rec.embedding = emb

                await session.commit()
                logger.info("✓ Evolved motion '%s' registered into PostgreSQL and synced.", motion_id)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not persist evolved motion to DB: %s", exc)

        return motion

    async def find_motion_for_phrase(self, phrase: str) -> MotionSpec | None:
        """Finds matching motion via hybrid search: exact stems + pgvector semantic retrieval."""
        lower = phrase.lower().strip()

        # 1. Fast-path: In-memory keyword match
        for motion in self._memory_cache.values():
            for kw in motion.keywords:
                clean_kw = kw.strip()
                if clean_kw and clean_kw in lower:
                    return motion

        # 2. pgvector semantic search in PostgreSQL for vast libraries
        query_emb = await self.get_embedding(phrase)
        if query_emb:
            try:
                async with AsyncSessionLocal() as session:
                    stmt = text("""
                        SELECT motion_id, category, intent_description, keywords, kinematic_spec
                        FROM stickman_motions
                        WHERE status = 'active' AND embedding IS NOT NULL
                        ORDER BY embedding <=> :emb
                        LIMIT 1;
                    """)
                    row = (await session.execute(stmt, {"emb": str(query_emb)})).fetchone()
                    if row:
                        spec = row[4] or {}
                        return MotionSpec(
                            motion_id=row[0],
                            category=row[1],
                            intent_description=row[2],
                            keywords=row[3] or [],
                            animation=spec.get("animation", "idle"),
                            eye_type=spec.get("eye_type", "neutral"),
                            mouth_type=spec.get("mouth_type", "smile"),
                            prop=spec.get("prop", "none"),
                            emoji=spec.get("emoji"),
                            custom_pose=spec.get("custom_pose"),
                        )
            except Exception as exc:  # noqa: BLE001
                logger.warning("pgvector search error: %s", exc)

        return None

    def _flush_cache_to_disk(self) -> None:
        """Serializes motion cache to disk for Remotion runtime and offline builds."""
        serializable = {
            m_id: asdict(m_spec) for m_id, m_spec in self._memory_cache.items()
        }
        json_str = json.dumps(serializable, ensure_ascii=False, indent=2)
        try:
            self.cache_path.write_text(json_str, encoding="utf-8")
            self.remotion_public_cache.write_text(json_str, encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not flush motion cache to disk: %s", exc)

    def load_cache_from_disk(self) -> int:
        """Loads cached motions from disk into RAM."""
        if self.cache_path.exists():
            try:
                data = json.loads(self.cache_path.read_text(encoding="utf-8"))
                for m_id, m_dict in data.items():
                    self._memory_cache[m_id] = MotionSpec(**m_dict)
                logger.info("Loaded %d motions from local cache.", len(self._memory_cache))
                return len(self._memory_cache)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not load motion cache: %s", exc)
        return 0
