"""Audience Retention Feedback Loop & Self-Evolution Engine for Jemini.

Evaluates post-publishing audience retention curves (3s hook, 15s midpoint,
and completion rates). Automatically deduces creative weaknesses, updates negative
prompt constraints, and persists learnings into PostgreSQL pgvector memory.
"""

import logging
from typing import Any

from sqlalchemy import select

from jemini.analytics.models import FeedbackAnalysisResult, PerformanceTier, RetentionMetrics
from jemini.storage.database import AsyncSessionLocal
from jemini.storage.models import AgentMemory, AgentMemoryCategory, ChannelAuditLog

logger = logging.getLogger(__name__)


class AudienceRetentionFeedbackLoop:
    """Closes the feedback loop between distribution metrics and future prompt synthesis."""

    # Retention Benchmarks for 9:16 Shorts
    BENCHMARK_HOOK_3S = 65.0       # Minimum 65% viewers remaining at 3s
    BENCHMARK_MIDPOINT_15S = 45.0  # Minimum 45% viewers remaining at 15s
    BENCHMARK_COMPLETION = 35.0    # Minimum 35% viewers watching full Short

    def __init__(self):
        self._local_negative_rules: dict[str, list[str]] = {}

    def analyze_metrics(self, metrics: RetentionMetrics) -> FeedbackAnalysisResult:
        """Analyzes retention drop-offs and constructs precise negative prompt adjustments."""
        weaknesses: list[str] = []
        learnings: list[str] = []
        neg_rules: list[str] = []

        # 1. Hook Analysis (0-3 seconds)
        if metrics.retention_at_3s < 50.0:
            weaknesses.append(f"Критичний провал хука: лише {metrics.retention_at_3s:.1f}% глядачів пройшли 3-тю секунду.")
            learnings.append("Перші 3 секунди повинні містити екстремальний парадокс або рух, без будь-яких привітань чи вступу.")
            neg_rules.append("ЗАБОРОНЕНО: починати з привітань, довгих пауз чи очевидних запитань у першій сцені.")
        elif metrics.retention_at_3s < self.BENCHMARK_HOOK_3S:
            weaknesses.append(f"Слабкий хук: {metrics.retention_at_3s:.1f}% (ціль: {self.BENCHMARK_HOOK_3S}%).")
            learnings.append("Посилити звуковий акцент (whoosh/glitch) та візуальний контраст на 0-й секунді.")
            neg_rules.append("УНИКАТИ: абстрактних назв чи нечітких хуків у сценарній відкривачці.")

        # 2. Midpoint Pacing Analysis (3-15 seconds)
        if metrics.retention_at_15s < self.BENCHMARK_MIDPOINT_15S:
            drop = metrics.retention_at_3s - metrics.retention_at_15s
            weaknesses.append(f"Провал у середині ролика: відтік {drop:.1f}% між 3-ю та 15-ю секундами.")
            learnings.append("Сцена розв'язання проблеми надто розтягнута або містить складну термінологію.")
            neg_rules.append("ЗАБОРОНЕНО: перевантажувати другу сцену академічними термінами чи монотонним текстом.")

        # 3. Completion & CTA Analysis
        if metrics.completion_rate < self.BENCHMARK_COMPLETION:
            weaknesses.append(f"Низький догляд до кінця: {metrics.completion_rate:.1f}% (ціль: {self.BENCHMARK_COMPLETION}%).")
            learnings.append("Фінал передбачуваний; заклик до дії (CTA) звучить занадто банально.")
            neg_rules.append("УНИКАТИ: стандартних фраз 'підпишись на канал'; інтегрувати CTA як інтригу наступного відео.")

        # Determine Tier
        if metrics.retention_at_3s >= 75.0 and metrics.completion_rate >= 45.0:
            tier = PerformanceTier.VIRAL
        elif not weaknesses:
            tier = PerformanceTier.HEALTHY
        elif metrics.retention_at_3s < 50.0 or metrics.completion_rate < 20.0:
            tier = PerformanceTier.CRITICAL
        else:
            tier = PerformanceTier.NEEDS_OPTIMIZATION

        # Cache rules in-memory
        if neg_rules:
            existing = self._local_negative_rules.setdefault(metrics.channel_id, [])
            for r in neg_rules:
                if r not in existing:
                    existing.append(r)

        return FeedbackAnalysisResult(
            performance_tier=tier,
            hook_score=metrics.retention_at_3s,
            pacing_score=metrics.retention_at_15s,
            retention_score=metrics.completion_rate,
            identified_weaknesses=weaknesses,
            actionable_learnings=learnings,
            negative_prompt_rules=neg_rules,
        )

    async def persist_learning_to_memory(
        self,
        metrics: RetentionMetrics,
        result: FeedbackAnalysisResult,
    ) -> bool:
        """Saves deduced insights into PostgreSQL pgvector AgentMemory and ChannelAuditLog."""
        if not result.actionable_learnings and not result.negative_prompt_rules:
            logger.info("No negative rules or learnings to persist for video %s.", metrics.video_id)
            return False

        content_body = (
            f"[RETENTION LEARNING for {metrics.channel_id} | Video {metrics.video_id}]\n"
            f"Performance Tier: {result.performance_tier.value.upper()}\n"
            f"Retention: 3s={metrics.retention_at_3s:.1f}%, 15s={metrics.retention_at_15s:.1f}%, End={metrics.completion_rate:.1f}%\n"
            f"Weaknesses: {'; '.join(result.identified_weaknesses)}\n"
            f"Actionable Insights: {'; '.join(result.actionable_learnings)}\n"
            f"Negative Prompt Rules: {'; '.join(result.negative_prompt_rules)}"
        )

        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    # 1. Store in AgentMemory
                    mem = AgentMemory(
                        channel_id=metrics.channel_id,
                        category=AgentMemoryCategory.EXPERIMENT_EXPERIENCE.value,
                        content=content_body,
                        metadata_json={
                            "video_id": metrics.video_id,
                            "tier": result.performance_tier.value,
                            "rules": result.negative_prompt_rules,
                        },
                    )
                    session.add(mem)

                    # 2. Record in Audit Log
                    audit = ChannelAuditLog(
                        channel_id=metrics.channel_id,
                        action="retention_feedback_learning",
                        status="success",
                        details={
                            "video_id": metrics.video_id,
                            "metrics": metrics.model_dump(mode="json"),
                            "rules_added": len(result.negative_prompt_rules),
                        },
                    )
                    session.add(audit)

                logger.info("✓ Persisted retention learning for channel '%s' to PostgreSQL.", metrics.channel_id)
                return True
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist feedback learning to DB (%s). In-memory caching preserved.", exc)
            return False

    async def get_active_negative_rules(self, channel_id: str) -> list[str]:
        """Fetches active negative prompt rules combining DB memories and in-memory cache."""
        rules = list(self._local_negative_rules.get(channel_id, []))

        try:
            async with AsyncSessionLocal() as session:
                query = select(AgentMemory).where(
                    AgentMemory.channel_id == channel_id,
                    AgentMemory.category == AgentMemoryCategory.EXPERIMENT_EXPERIENCE.value,
                ).order_by(AgentMemory.id.desc()).limit(5)
                res = await session.execute(query)
                records = res.scalars().all()
                for rec in records:
                    db_rules: list[Any] = rec.metadata_json.get("rules", [])
                    for r in db_rules:
                        if isinstance(r, str) and r not in rules:
                            rules.append(r)
        except Exception as exc:  # noqa: BLE001
            logger.debug("Database lookup for negative rules skipped (%s), using local rules.", exc)

        return rules
