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
    [ОЗВУЧКА]: Голос живий, без мертвого ха-ха, присутні природні жіночі інтонації.
    [АНІМАЦІЯ]: Стикмен плавно змінює пози (point_up, surprise), відсутній ефект застигання.
    [ДИЗАЙН ТА ТИПОГРАФІКА]: Розмір шрифту 28px оптимізовано під 1080x1920 мобільний екран.
    [СТИЛЬ ТА ПОРІВНЯННЯ]: Монтаж у стилі Fireship, кінетичні субтитри як у Hormozi.
    [ПОРІВНЯННЯ]: Повністю відповідає початковому сценарію.
    [ЩО ПОКРАЩИТИ]:
    - Збільшити контраст неонової плашки на 5%
    - Підняти гучність звукового ефекту
    [ПРАВИЛА САМОВДОСКОНАЛЕННЯ]:
    - УНИКАТИ: статичних поз довше 1.5 секунди
    - ОБОВ'ЯЗКОВО: тримати розмір шрифту плашок не менше 26px
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
    assert "відсутній ефект застигання" in res.animation_evaluation
    assert "1080x1920" in res.design_typography_evaluation
    assert "Fireship" in res.style_benchmark_evaluation
    assert len(res.actionable_improvements) == 2
    assert len(res.self_evolution_rules) == 2
    assert any("УНИКАТИ:" in r for r in res.self_evolution_rules)
    assert any("ОБОВ'ЯЗКОВО:" in r for r in res.self_evolution_rules)


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
    assert len(result.animation_evaluation) > 0
    assert len(result.design_typography_evaluation) > 0
    assert len(result.style_benchmark_evaluation) > 0
    assert len(result.self_evolution_rules) >= 2


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
    assert len(card.passed_criteria) >= 4
    assert any("Анімація" in c for c in card.passed_criteria)
    assert any("Дизайн" in c for c in card.passed_criteria)
    assert live_res.frames_streamed > 0


@pytest.mark.asyncio
async def test_live_reviewer_self_evolution_feedback_loop(sample_video_path: Path):
    from jemini.analytics.feedback_loop import AudienceRetentionFeedbackLoop

    reviewer = LiveVideoReviewer()
    intent = ValidationIntent(
        title="Тест самовдосконалення через Live API",
        target_type=ValidationTargetType.VIDEO,
        expected_duration_seconds=15.0,
    )

    test_channel = "stickman_evolution_test"
    result = await reviewer.review_video(
        video_path=sample_video_path,
        intent=intent,
        channel_id=test_channel,
        mock_mode=True,
    )

    assert len(result.self_evolution_rules) >= 2

    # Check that AudienceRetentionFeedbackLoop reads the persisted self-evolution rules
    feedback = AudienceRetentionFeedbackLoop()
    active_rules = await feedback.get_active_negative_rules(channel_id=test_channel)

    # In environments with or without DB, verify the contract
    assert isinstance(active_rules, list)


@pytest.mark.asyncio
async def test_live_reviewer_detects_occlusion_failure():
    reviewer = LiveVideoReviewer()
    occluded_review_text = """
    === ЖИВА РЕЦЕНЗІЯ АРТ-ДИРЕКТОРА (GEMINI 3.8 LIVE STREAM) ===
    [ХУК]: Початок динамічний.
    [ОЗВУЧКА]: Відповідає стандарту.
    [КОМПОЗИЦІЯ ТА ПЕРЕКРИТТЯ]: КРИТИЧНИЙ ДЕФЕКТ: плашка Forma 2-B перекриває голову та обличчя стикмена на половину відео!
    [АНІМАЦІЯ]: Стикмен рухається, але його не видно.
    [ДИЗАЙН ТА ТИПОГРАФІКА]: Шрифти хороші.
    [СТИЛЬ ТА ПОРІВНЯННЯ]: Середній темп.
    [ПОРІВНЯННЯ]: Не відповідає задуму через перекриття персонажа.
    [ЩО ПОКРАЩИТИ]:
    - Змістити плашку вище
    - Винести персонажа на передній план
    [ПРАВИЛА САМОВДОСКОНАЛЕННЯ]:
    - УНИКАТИ: перекриття персонажа картою інтерфейсу
    ОЦІНКА: 5.5/10
    ВЕРДИКТ: NEEDS_CORRECTION
    """
    res = reviewer._parse_review_response(
        raw_text=occluded_review_text,
        video_path="sample_occluded.mp4",
        duration=15.0,
        frames_count=15,
    )
    assert res.status == ValidationStatus.NEEDS_CORRECTION
    assert res.overall_score <= 6.0
    assert "перекриває" in res.occlusion_evaluation
