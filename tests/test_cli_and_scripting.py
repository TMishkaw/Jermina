from pathlib import Path

import pytest

from jemini.cli.main import run_e2e_render, run_test_readiness
from jemini.rendering.remotion_renderer import RemotionRenderer, RenderOptions
from jemini.scripting.generator import ScriptGenerator


@pytest.mark.asyncio
async def test_script_generator_mock():
    gen = ScriptGenerator()
    script = await gen.generate_script(topic="Тест автономного кодингу", mock_mode=True)

    assert script.title
    assert script.hook_text
    assert len(script.scenes) == 4
    assert script.scenes[0].scene_id == "scene_01_hook"
    assert "whoosh" in script.scenes[0].expected_sfx
    assert script.scenes[3].scene_id == "scene_04_cta"


def test_remotion_renderer_stickman_cues():
    renderer = RemotionRenderer()
    cues = renderer.generate_stickman_cues(total_frames=360)

    assert len(cues) == 4
    assert cues[0]["animation"] == "surprised"
    assert cues[1]["animation"] == "talk"
    assert cues[2]["animation"] == "laugh"
    assert cues[3]["animation"] == "point_up"


@pytest.mark.asyncio
async def test_remotion_renderer_dry_run(tmp_path: Path):
    renderer = RemotionRenderer()
    out_mp4 = tmp_path / "test_out.mp4"

    res = await renderer.render_short(
        title="Test Title",
        hook_text="TEST HOOK",
        audio_path=tmp_path / "mock.wav",
        audio_rms=[0.1, 0.2, 0.3],
        subtitles=[{"text": "Test", "startFrame": 0, "endFrame": 30}],
        output_mp4=out_mp4,
        options=RenderOptions(dry_run=True),
    )

    assert res.exists()
    assert res == out_mp4


@pytest.mark.asyncio
async def test_e2e_pipeline_render_mock(tmp_path: Path):
    summary = await run_e2e_render(
        topic="Штучний інтелект для відео",
        output_dir=tmp_path,
        mock_mode=True,
        skip_validation=False,
    )

    assert summary["title"]
    assert Path(summary["video_path"]).exists()
    assert summary["duration_seconds"] > 0
    assert summary["total_frames"] > 0
    assert summary["validation_score"] is not None
    assert (tmp_path / "pipeline_summary.json").exists()


@pytest.mark.asyncio
async def test_readiness_suite():
    readiness = await run_test_readiness()
    assert isinstance(readiness, bool)
