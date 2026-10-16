"""Unit tests for Audience Retention Feedback Loop and Self-Evolution."""

import pytest

from jemini.analytics.feedback_loop import AudienceRetentionFeedbackLoop
from jemini.analytics.models import PerformanceTier, RetentionMetrics


def test_feedback_analysis_viral():
    loop = AudienceRetentionFeedbackLoop()
    metrics = RetentionMetrics(
        video_id="vid_viral_01",
        channel_id="stickman_lab",
        total_views=50000,
        retention_at_3s=82.0,
        retention_at_15s=65.0,
        completion_rate=52.0,
    )
    result = loop.analyze_metrics(metrics)

    assert result.performance_tier == PerformanceTier.VIRAL
    assert len(result.identified_weaknesses) == 0
    assert len(result.negative_prompt_rules) == 0


def test_feedback_analysis_critical_hook_failure():
    loop = AudienceRetentionFeedbackLoop()
    metrics = RetentionMetrics(
        video_id="vid_failed_01",
        channel_id="stickman_lab",
        total_views=1500,
        retention_at_3s=42.0,
        retention_at_15s=30.0,
        completion_rate=18.0,
    )
    result = loop.analyze_metrics(metrics)

    assert result.performance_tier == PerformanceTier.CRITICAL
    assert len(result.identified_weaknesses) >= 2
    assert any("провал хука" in w.lower() for w in result.identified_weaknesses)
    assert len(result.negative_prompt_rules) > 0
    assert any("ЗАБОРОНЕНО" in r for r in result.negative_prompt_rules)


@pytest.mark.asyncio
async def test_feedback_loop_rules_lifecycle():
    loop = AudienceRetentionFeedbackLoop()
    channel = "cyber_matrix"
    metrics = RetentionMetrics(
        video_id="vid_cyber_drop",
        channel_id=channel,
        retention_at_3s=48.0,
        retention_at_15s=28.0,
        completion_rate=20.0,
    )
    result = loop.analyze_metrics(metrics)

    # In-memory cached rules
    active_rules = await loop.get_active_negative_rules(channel)
    assert len(active_rules) > 0

    # Persist to database (if PostgreSQL is online)
    persisted = await loop.persist_learning_to_memory(metrics, result)
    # Even if DB fails in isolated environments, loop returns boolean without throwing
    assert isinstance(persisted, bool)
