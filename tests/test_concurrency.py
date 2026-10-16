import wave
from pathlib import Path

import pytest

from jemini.orchestration.limits import PipelineLimits
from jemini.orchestration.parallel_pipeline import (
    ParallelMediaOrchestrator,
    SceneScript,
)
from jemini.voice.live_voice_service import VoiceArchetype, VoiceDirective


def test_pipeline_limits_configuration():
    assert PipelineLimits.LIVE.audio_only_max_minutes == 15.0
    assert PipelineLimits.LIVE.audio_video_max_minutes == 2.0
    assert PipelineLimits.LIVE.connection_lifetime_minutes == 10.0
    assert PipelineLimits.LIVE.max_safe_scene_words == 180
    assert PipelineLimits.LIVE.sample_rate_output_hz == 24000
    assert PipelineLimits.MODELS.flash_lite_rpd == 500
    assert PipelineLimits.REMOTION.default_concurrency_workers == 4


@pytest.mark.asyncio
async def test_parallel_pipeline_execution(tmp_path: Path):
    orchestrator = ParallelMediaOrchestrator()

    scenes = [
        SceneScript(
            scene_id="scene_01_hook",
            text="Перша сцена: захоплюючий хук з неймовірною динамікою!",
            directive=VoiceDirective(archetype=VoiceArchetype.ZEPHYR, emotion="commanding"),
            expected_sfx=["whoosh"],
        ),
        SceneScript(
            scene_id="scene_02_body",
            text="Друга сцена: глибокий аналіз та несподівані факти.",
            directive=VoiceDirective(archetype=VoiceArchetype.AOEDE, vocal_fry=True),
            expected_sfx=["pop", "whoosh"],
        ),
        SceneScript(
            scene_id="scene_03_cta",
            text="Третя сцена: підпишіться на канал та тисніть дзвіночок!",
            directive=VoiceDirective(archetype=VoiceArchetype.ZEPHYR),
            expected_sfx=["chime"],
        ),
    ]

    result = await orchestrator.execute_parallel_pipeline(
        scenes=scenes,
        output_dir=tmp_path,
        mock_mode=True,
    )

    # Verify master audio
    assert Path(result.master_audio_path).exists()
    assert result.total_duration_seconds > 0
    assert result.total_frames > 0
    assert len(result.scene_audios) == 3

    # Check WAV properties
    with wave.open(result.master_audio_path, "rb") as wf:
        assert wf.getframerate() == 24000
        assert wf.getnchannels() == 1
        assert wf.getsampwidth() == 2

    # Verify SFX generation
    assert "whoosh" in result.generated_sfx
    assert "pop" in result.generated_sfx
    assert "chime" in result.generated_sfx
    for sfx_path in result.generated_sfx.values():
        assert Path(sfx_path).exists()

    # Verify unified cues frame offsets
    assert len(result.unified_cues) > 0
    first_cue = result.unified_cues[0]
    last_cue = result.unified_cues[-1]
    assert first_cue["startFrame"] >= 0
    assert last_cue["endFrame"] <= result.total_frames
    assert last_cue["startFrame"] > first_cue["startFrame"]

    # Verify RMS frames
    assert len(result.audio_rms_per_frame) == result.total_frames


@pytest.mark.asyncio
async def test_parallel_pipeline_empty_scenes_guard(tmp_path: Path):
    orchestrator = ParallelMediaOrchestrator()
    with pytest.raises(ValueError, match="At least one scene is required"):
        await orchestrator.execute_parallel_pipeline(scenes=[], output_dir=tmp_path)


def test_scene_safe_limit_warning(caplog):
    orchestrator = ParallelMediaOrchestrator()
    long_text = "слово " * 185
    scene = SceneScript(scene_id="scene_long", text=long_text)

    with caplog.at_level("WARNING"):
        orchestrator._validate_scene_limits(scene)

    assert "exceeding safe limit of 180" in caplog.text
