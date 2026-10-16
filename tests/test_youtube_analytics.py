"""Unit tests for YouTube Channel Ingestor and Audience Sentiment Analyzer."""

import pytest

from jemini.analytics.comment_analyzer import (
    AudienceSentimentAnalyzer,
    BatchAnalysisResult,
    CommentAnalysisItem,
)
from jemini.analytics.youtube_ingestor import YouTubeChannelIngestor


def test_youtube_duration_parser():
    """Verifies ISO 8601 duration parser across standard video durations."""
    # We instantiate a dummy object or test the method directly
    parser = YouTubeChannelIngestor.__new__(YouTubeChannelIngestor)

    assert parser._parse_duration_seconds("PT58S") == 58.0
    assert parser._parse_duration_seconds("PT1M") == 60.0
    assert parser._parse_duration_seconds("PT1M30S") == 90.0
    assert parser._parse_duration_seconds("PT2H15M10S") == 2 * 3600 + 15 * 60 + 10
    assert parser._parse_duration_seconds("") == 0.0
    assert parser._parse_duration_seconds(None) == 0.0
    assert parser._parse_duration_seconds("INVALID") == 0.0


def test_comment_analysis_schemas():
    """Validates strict Pydantic schemas for comment analysis and batch responses."""
    item = CommentAnalysisItem(
        comment_id="c_123",
        sentiment="question",
        audience_topic="Субтитри та шрифт",
        witty_reply_suggestion="Шрифт вже підтягнули!",
    )
    assert item.sentiment == "question"
    assert item.audience_topic == "Субтитри та шрифт"

    batch = BatchAnalysisResult(
        analyzed_comments=[item],
        viral_hypotheses=["Чому шрифти ламаються в Shorts", "Як зробити ідеальні субтитри"],
    )
    assert len(batch.analyzed_comments) == 1
    assert len(batch.viral_hypotheses) == 2


@pytest.mark.asyncio
async def test_sentiment_analyzer_mock_mode():
    """Verifies AudienceSentimentAnalyzer mock mode without consuming API quota."""
    analyzer = AudienceSentimentAnalyzer(batch_size=10)

    # In mock mode, analyze_comments processes DB rows if any or returns safe fallback
    report = await analyzer.analyze_comments(
        channel_id="UC1ol6l3KL3sgmLPiwQy2QTA",
        limit=20,
        enqueue_hypotheses=False,
        mock_mode=True,
    )

    assert report is not None
    assert isinstance(report.total_analyzed, int)
    assert isinstance(report.sentiment_distribution, dict)
    assert isinstance(report.generated_hypotheses, list)
    assert isinstance(report.top_audience_topics, list)
