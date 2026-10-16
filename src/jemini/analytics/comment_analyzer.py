"""Audience Sentiment & Comment Analyzer Engine.

Performs semantic analysis of viewer comments from YouTube Data API dump / PostgreSQL,
identifies sentiment distribution, extracts audience pain-points and questions,
and autonomously generates viral video hypotheses to fuel the Production Queue.
Uses gemini-3.1-flash-lite (high-quota 500 RPD) with compact batching to preserve tokens.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from sqlalchemy import select, update

from jemini.core.config import settings
from jemini.rotator.rotator import APIKeyRotator
from jemini.scheduling.queue import ProductionQueue
from jemini.storage.database import AsyncSessionLocal
from jemini.storage.models import YouTubeCommentRecord

logger = logging.getLogger(__name__)


class CommentAnalysisItem(BaseModel):
    """Semantic analysis of an individual viewer comment."""
    comment_id: str
    sentiment: str = Field(description="positive, neutral, negative, question, or feature_request")
    audience_topic: str | None = Field(default=None, description="Extracted core theme, question, or pain-point")
    witty_reply_suggestion: str | None = Field(default=None, description="Sharp, in-character AI host reply")


class BatchAnalysisResult(BaseModel):
    """Structured batch response from Gemini Flash-Lite."""
    analyzed_comments: list[CommentAnalysisItem] = Field(default_factory=list)
    viral_hypotheses: list[str] = Field(
        default_factory=list,
        description="2-3 fresh video topic hypotheses inspired by viewer questions and feedback",
    )


class AudienceSentimentReport(BaseModel):
    """Consolidated sentiment and topic intelligence report."""
    total_analyzed: int
    sentiment_distribution: dict[str, int] = Field(default_factory=dict)
    top_audience_topics: list[str] = Field(default_factory=list)
    generated_hypotheses: list[str] = Field(default_factory=list)
    enqueued_task_ids: list[str] = Field(default_factory=list)


class AudienceSentimentAnalyzer:
    """Batch semantic analyzer for audience comments and viral hypothesis generation."""

    def __init__(
        self,
        rotator: APIKeyRotator | None = None,
        model_name: str = "gemini-3.1-flash-lite",
        batch_size: int = 25,
    ):
        self.rotator = rotator
        self.model_name = model_name
        self.batch_size = batch_size

    def _build_batch_prompt(self, comments: list[dict[str, Any]]) -> str:
        comments_formatted = []
        for c in comments:
            comments_formatted.append({
                "id": c["comment_id"],
                "author": c["author_name"],
                "text": c["text"],
                "likes": c.get("like_count", 0),
            })

        return (
            "Ти — Головний Data Scientist, Сценарист та Стендап-редактор YouTube-каналу @Jermina_AI про штучний інтелект.\n"
            "Твоє завдання — проаналізувати пачку реальних коментарів глядачів, визначити їхній сентимент, "
            "вилучити запитання/болі аудиторії та сформулювати нові вірусні теми для майбутніх Shorts.\n\n"
            f"=== КОМЕНТАРІ ГЛЯДАЧІВ ({len(comments)} шт.) ===\n"
            f"{json.dumps(comments_formatted, ensure_ascii=False, indent=2)}\n\n"
            "ІНСТРУКЦІЯ:\n"
            "1. Для кожного коментаря визнач sentiment: 'positive', 'neutral', 'negative', 'question' або 'feature_request'.\n"
            "2. Якщо в коментарі є ідея, запитання чи зауваження (наприклад, про субтитри, смайлики, нові моделі, баги) — вкажи це в audience_topic.\n"
            "3. Згенеруй 2-3 яскраві, провокативні, вірусні теми/гіпотези для наступних роликів (viral_hypotheses) на основі цих запитань.\n\n"
            "ФОРМАТ ВІДПОВІДІ (ТІЛЬКИ ВАЛІДНИЙ JSON):\n"
            "{\n"
            '  "analyzed_comments": [\n'
            '    {\n'
            '      "comment_id": "ідентифікатор коментаря",\n'
            '      "sentiment": "positive/neutral/negative/question/feature_request",\n'
            '      "audience_topic": "тема/питання або null",\n'
            '      "witty_reply_suggestion": "дотепна відповідь або null"\n'
            '    }\n'
            '  ],\n'
            '  "viral_hypotheses": [\n'
            '    "Вірусна назва ролика 1",\n'
            '    "Вірусна назва ролика 2"\n'
            '  ]\n'
            "}"
        )

    async def analyze_comments(
        self,
        channel_id: str = "UC1ol6l3KL3sgmLPiwQy2QTA",
        limit: int = 100,
        enqueue_hypotheses: bool = True,
        mock_mode: bool = False,
    ) -> AudienceSentimentReport:
        """Fetches pending comments from PostgreSQL, processes them in batches of 25, and updates DB."""
        logger.info("Fetching comments for sentiment analysis (channel: %s)...", channel_id)

        # 1. Fetch unanalyzed viewer comments from DB
        comments_to_analyze: list[dict[str, Any]] = []
        async with AsyncSessionLocal() as session:
            stmt = (
                select(YouTubeCommentRecord)
                .where(
                    YouTubeCommentRecord.sentiment.is_(None),
                    YouTubeCommentRecord.author_name.notin_(["@Jermina_AI", "Jermina AI Studio"]),
                )
                .limit(limit)
            )
            rows = (await session.execute(stmt)).scalars().all()

            for r in rows:
                clean_text = r.text.strip()
                if len(clean_text) < 3:
                    continue
                comments_to_analyze.append({
                    "comment_id": r.comment_id,
                    "video_id": r.video_id,
                    "author_name": r.author_name,
                    "text": clean_text,
                    "like_count": r.like_count,
                })

        logger.info("Found %d meaningful viewer comments to analyze", len(comments_to_analyze))
        if not comments_to_analyze:
            return AudienceSentimentReport(
                total_analyzed=0,
                sentiment_distribution={},
                top_audience_topics=[],
                generated_hypotheses=[],
                enqueued_task_ids=[],
            )

        all_analyzed_items: list[CommentAnalysisItem] = []
        all_hypotheses: list[str] = []

        # 2. Process in batches
        for i in range(0, len(comments_to_analyze), self.batch_size):
            batch = comments_to_analyze[i : i + self.batch_size]
            logger.info("Analyzing batch %d-%d of %d comments via %s...",
                        i + 1, min(i + self.batch_size, len(comments_to_analyze)),
                        len(comments_to_analyze), self.model_name)

            if mock_mode or not settings.gemini_api_keys:
                # Deterministic mock analysis
                mock_items = [
                    CommentAnalysisItem(
                        comment_id=c["comment_id"],
                        sentiment="question" if "?" in c["text"] else "positive",
                        audience_topic="Якість субтитрів та емодзі" if "смайл" in c["text"].lower() else "Генерація контенту",
                        witty_reply_suggestion="Дякую за фідбек! Ми вже покращуємо таймінги.",
                    )
                    for c in batch
                ]
                mock_res = BatchAnalysisResult(
                    analyzed_comments=mock_items,
                    viral_hypotheses=[
                        "Чому ШІ плутає емодзі в текстах: експеримент з токенами",
                        "Як вичистити артефакти субтитрів за 3 секунди",
                    ],
                )
            else:
                # Resilient multi-model & key-rotation execution loop
                candidate_models = [self.model_name, "gemini-3-flash-preview", "gemini-3.5-flash-lite", "gemini-3.8-flash"]
                # Deduplicate while preserving order
                seen_models = set()
                ordered_models = [m for m in candidate_models if not (m in seen_models or seen_models.add(m))]

                prompt = self._build_batch_prompt(batch)
                batch_success = False
                last_error: Exception | None = None

                for model_candidate in ordered_models:
                    # Try keys from rotator or settings pool
                    keys_to_try = settings.gemini_api_keys or [""]
                    for key in keys_to_try:
                        try:
                            client = genai.Client(api_key=key)
                            config = types.GenerateContentConfig(
                                response_mime_type="application/json",
                                temperature=0.3,
                            )
                            response = client.models.generate_content(
                                model=model_candidate,
                                contents=prompt,
                                config=config,
                            )
                            # Clean possible markdown wrapping if returned
                            resp_text = response.text.strip()
                            resp_text = resp_text.removeprefix("```json")
                            resp_text = resp_text.removesuffix("```")
                            data = json.loads(resp_text.strip())
                            mock_res = BatchAnalysisResult.model_validate(data)
                            batch_success = True
                            logger.info("✓ Batch successfully analyzed using model '%s'", model_candidate)
                            break
                        except Exception as exc:  # noqa: BLE001
                            last_error = exc
                            logger.warning(
                                "Model '%s' failed with key %s...: %s. Trying next...",
                                model_candidate,
                                key[:6] if key else "none",
                                exc,
                            )
                    if batch_success:
                        break

                if not batch_success:
                    logger.error("All candidate models and keys exhausted for batch: %s", last_error)
                    raise last_error or RuntimeError("Failed to analyze comments batch")

            all_analyzed_items.extend(mock_res.analyzed_comments)
            all_hypotheses.extend(mock_res.viral_hypotheses)

        # 3. Update PostgreSQL with Analyzed Sentiment
        logger.info("Saving %d sentiment records to PostgreSQL...", len(all_analyzed_items))
        async with AsyncSessionLocal() as session:
            for item in all_analyzed_items:
                stmt_up = (
                    update(YouTubeCommentRecord)
                    .where(YouTubeCommentRecord.comment_id == item.comment_id)
                    .values(
                        sentiment=item.sentiment,
                        audience_topic=item.audience_topic,
                        analyzed_at=datetime.now(timezone.utc).replace(tzinfo=None),
                    )
                )
                await session.execute(stmt_up)
            await session.commit()

        # 4. Enqueue Viral Hypotheses into ProductionQueue
        enqueued_ids: list[str] = []
        unique_hypotheses = list(dict.fromkeys(all_hypotheses))
        if enqueue_hypotheses and unique_hypotheses:
            queue = ProductionQueue()
            for topic in unique_hypotheses:
                task = queue.enqueue(
                    channel_id="cyber_matrix",
                    topic=topic,
                    metadata={"source": "audience_sentiment_loop", "origin_channel": "@Jermina_AI"},
                )
                enqueued_ids.append(task.task_id)
            logger.info("✓ Enqueued %d viral hypotheses into Production Queue: %s", len(enqueued_ids), enqueued_ids)

        # 5. Compile Statistics
        distribution: dict[str, int] = {}
        for item in all_analyzed_items:
            distribution[item.sentiment] = distribution.get(item.sentiment, 0) + 1

        top_topics = [
            it.audience_topic for it in all_analyzed_items if it.audience_topic
        ]
        unique_topics = list(dict.fromkeys(top_topics))[:8]

        report = AudienceSentimentReport(
            total_analyzed=len(all_analyzed_items),
            sentiment_distribution=distribution,
            top_audience_topics=unique_topics,
            generated_hypotheses=unique_hypotheses,
            enqueued_task_ids=enqueued_ids,
        )
        logger.info("✓ Audience Sentiment Analysis completed successfully!")
        return report
