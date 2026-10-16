import wave
from pathlib import Path

from jemini.media.assets_hub import MediaAssetsHub, ProceduralSFXGenerator


def test_procedural_sfx_generation(tmp_path: Path):
    whoosh_path = tmp_path / "whoosh.wav"
    pop_path = tmp_path / "pop.wav"
    hit_path = tmp_path / "hit.wav"
    chime_path = tmp_path / "chime.wav"

    ProceduralSFXGenerator.generate_whoosh(whoosh_path)
    ProceduralSFXGenerator.generate_pop(pop_path)
    ProceduralSFXGenerator.generate_hit(hit_path)
    ProceduralSFXGenerator.generate_chime(chime_path)

    for p in (whoosh_path, pop_path, hit_path, chime_path):
        assert p.exists()
        with wave.open(str(p), "rb") as wf:
            assert wf.getframerate() == 44100
            assert wf.getnchannels() == 1
            assert wf.getsampwidth() == 2
            assert wf.getnframes() > 0


def test_media_assets_hub(tmp_path: Path):
    hub = MediaAssetsHub(assets_dir=tmp_path)

    # 1. On-demand procedural generation
    sfx = hub.get_or_create_sfx("cinematic_hit")
    assert sfx.exists()
    assert sfx.name == "cinematic_hit.wav"

    # 2. Discovery
    assets = hub.list_all_assets()
    assert len(assets) >= 1
    assert any(a.name == "cinematic_hit" for a in assets)
