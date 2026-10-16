import pytest

from jemini.validation.models import (
    ValidationIntent,
    ValidationStatus,
    ValidationTargetType,
)
from jemini.validation.validator import MediaValidationEngine


@pytest.mark.asyncio
async def test_validation_engine_card_generation():
    engine = MediaValidationEngine()
    intent = ValidationIntent(
        title="Sample Stickman Short Hook",
        target_type=ValidationTargetType.VIDEO,
        expected_duration_seconds=15.0,
        target_emotion="high energy",
        key_points=["3s viral hook", "crisp karaoke text"],
    )

    card = await engine.validate(
        intent=intent,
        payload_summary="Ролик триває 15 секунд, має потужний 3-секундний хук 'СТОП!' та плавні субтитри.",
        mock_mode=True,
    )

    assert card.target_type == ValidationTargetType.VIDEO
    assert card.status == ValidationStatus.PASSED
    assert card.overall_score >= 8.0
    assert len(card.passed_criteria) > 0


@pytest.mark.asyncio
async def test_autonomous_correction_loop():
    engine = MediaValidationEngine()
    intent = ValidationIntent(
        title="Voice Speech Review",
        target_type=ValidationTargetType.AUDIO_VOICE,
        target_emotion="playful laughing",
    )

    attempts = 0

    async def mock_generator(correction_prompt: str | None):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            # First attempt has defect
            return "audio_file_v1.wav", "Виявлено дефект: монотонна інтонація без живих емоцій"
        # Second attempt corrected
        return "audio_file_v2.wav", "Ідеальна акторська гра, vocal fry та живий сміх за стандартом"

    final_card, final_artifact = await engine.execute_quality_loop(
        intent=intent,
        generator_fn=mock_generator,
        max_iterations=3,
        mock_mode=True,
    )

    assert attempts == 2
    assert final_card.status == ValidationStatus.PASSED
    assert final_artifact == "audio_file_v2.wav"
    assert final_card.iteration == 2
