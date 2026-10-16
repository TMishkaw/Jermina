from jemini.rendering.remotion_renderer import RemotionRenderer


def test_stickman_cues_coverage():
    """Ensures cues cover 100% of duration without gaps or freezing."""
    renderer = RemotionRenderer()
    for duration in [300, 450, 600, 900]:
        cues = renderer.generate_stickman_cues(total_frames=duration)
        assert len(cues) > 0

        # Frame continuity
        expected_start = 0
        for cue in cues:
            assert cue["fromFrame"] == expected_start
            assert cue["durationInFrames"] > 0
            assert cue["animation"] in ["surprised", "talk", "point_up", "laugh", "celebrate"]
            assert cue["eyeType"] in ["wide", "neutral", "happy", "wink"]
            assert cue["mouthType"] in ["gasp", "talking", "smile"]
            expected_start += cue["durationInFrames"]

        assert expected_start == duration
