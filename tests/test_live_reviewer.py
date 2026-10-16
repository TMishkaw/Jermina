from pathlib import Path

import pytest

from jemini.rotator.rotator import APIKeyRotator
from jemini.validation.live_reviewer import LiveVideoReviewer
from jemini.validation.models import (
    ValidationIntent,
    ValidationStatus,
    ValidationTargetType,
)
from jemini.validation.validator import MediaValidationEngine


@pytest.fixture
def sample_video_path() -> Path:
    """Returns path to the existing rendered MP4 test video."""
    video = Path("output/live_production/test_render.mp4").resolve()
    assert video.exists(), f"Sample test video must exist at {video}"
    return video


@pytest.mark.asyncio
async def test_live_reviewer_parse_response():
    reviewer = LiveVideoReviewer()
    raw_text = """
    === ЖИВА РЕЦЕНЗІЯ АРТ-ДИРЕКТОРА (GEMINI 3.8 LIVE STREAM) ===
    [ХУК]: Перші 3 секунди тримають увагу ідеально, різкий неоновий спалах.
    [ОЗВУЧКА]: Голос живий, без мертвого ха-ха, присутні природні вдихи.
    [ВІЗУАЛ]: Субтитри вирівняні, динамічний стикмен.
    [ПОРІВНЯННЯ]: Повністю відповідає початковому сценарію.
    [ЩО ПОКРАЩИТИ]:
    - Збільшити шрифт субтитрів на 10%
    - Підняти гучність звукового ефекту
    ОЦІНКА: 9.4/10
    ВЕРДИКТ: PASSED
    """
    res = reviewer._parse_review_response(
        raw_text=raw_text,
        video_path="sample.mp4",
        duration=15.0,
        frames_count=15,
    )
    assert res.overall_score == 9.4
    assert res.status == ValidationStatus.PASSED
    assert "неоновий спалах" in res.hook_evaluation
    assert "без мертвого ха-ха" in res.voice_acting_evaluation
    assert len(res.actionable_improvements) == 2


@pytest.mark.asyncio
async def test_live_reviewer_mock_review(sample_video_path: Path):
    reviewer = LiveVideoReviewer()
    intent = ValidationIntent(
        title="Тест квантового комп'ютера",
        target_type=ValidationTargetType.VIDEO,
        expected_duration_seconds=24.0,
        key_points=["3-second hook", "clear graphics", "24kHz voice"],
    )

    result = await reviewer.review_video(
        video_path=sample_video_path,
        intent=intent,
        channel_id="test_channel",
        mock_mode=True,
    )

    assert result.video_path == str(sample_video_path)
    assert result.frames_streamed > 0
    assert result.audio_streamed_seconds > 0.0
    assert result.overall_score >= 8.0
    assert result.status == ValidationStatus.PASSED
    assert len(result.actionable_improvements) > 0


@pytest.mark.asyncio
async def test_media_validation_engine_live_stream_integration(sample_video_path: Path):
    rotator = APIKeyRotator()
    engine = MediaValidationEngine(rotator=rotator)
    intent = ValidationIntent(
        title="Live Stream Integration Check",
        target_type=ValidationTargetType.VIDEO,
        expected_duration_seconds=24.0,
    )

    card, live_res = await engine.validate_video_live_stream(
        intent=intent,
        video_path=sample_video_path,
        channel_id="stickman_lab",
        mock_mode=True,
    )

    assert card.target_type == ValidationTargetType.VIDEO
    assert card.status == ValidationStatus.PASSED
    assert card.overall_score == live_res.overall_score
    assert len(card.passed_criteria) >= 2
    assert live_res.frames_streamed > 0
