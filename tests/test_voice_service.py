import wave
from pathlib import Path

import pytest

from jemini.voice.live_voice_service import (
    GeminiLiveVoiceService,
    VoiceArchetype,
    VoiceDirective,
)


@pytest.mark.asyncio
async def test_live_voice_service_mock_synthesis(tmp_path: Path):
    service = GeminiLiveVoiceService()
    test_wav = tmp_path / "test_voice.wav"

    directive = VoiceDirective(
        archetype=VoiceArchetype.ZEPHYR,
        emotion="energetic, laughing",
        vocal_fry=True,
    )

    result = await service.synthesize(
        text_to_speak="Привіт усім! Це тестовий запуск голосу Jemini.",
        output_wav_path=test_wav,
        directive=directive,
        mock_mode=True,
    )

    assert Path(result.audio_path).exists()
    assert result.sample_rate == 24000
    assert result.channels == 1
    assert result.duration_seconds > 0
    assert len(result.audio_rms_per_frame) > 0
    assert len(result.suggested_cues) > 0

    # Verify standard WAV header
    with wave.open(str(test_wav), "rb") as wf:
        assert wf.getframerate() == 24000
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2
