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


def test_kinematic_presets_symmetry_and_angles():
    """Regression test ensuring two-handed gestures have balanced opposite shoulder angles."""
    from pathlib import Path
    import re

    presets_file = Path("remotion/src/components/kinematic_presets.ts")
    assert presets_file.exists(), "kinematic_presets.ts must exist"
    content = presets_file.read_text(encoding="utf-8")

    # 1. heart_hands must have opposite shoulder angles
    heart_match = re.search(r'case "heart_hands":.*?leftShoulderAngle:\s*(-?\d+).*?rightShoulderAngle:\s*(-?\d+)', content, re.DOTALL)
    assert heart_match, "heart_hands must define shoulder angles"
    left_sh, right_sh = int(heart_match.group(1)), int(heart_match.group(2))
    assert left_sh < 0 and right_sh > 0, "heart_hands must arch outward symmetrically (-left, +right)"

    # 2. shrug must have opposite shoulder angles
    shrug_match = re.search(r'case "shrug":.*?leftShoulderAngle:\s*(-?\d+).*?rightShoulderAngle:\s*(-?\d+)', content, re.DOTALL)
    assert shrug_match, "shrug must define shoulder angles"
    left_sh, right_sh = int(shrug_match.group(1)), int(shrug_match.group(2))
    assert left_sh < 0 and right_sh > 0, "shrug must spread outward symmetrically (-left, +right)"

    # 3. explain must have opposite shoulder angles
    explain_match = re.search(r'case "explain":.*?leftShoulderAngle:\s*(-?\d+).*?rightShoulderAngle:\s*(-?\d+)', content, re.DOTALL)
    assert explain_match, "explain must define shoulder angles"
    left_sh, right_sh = int(explain_match.group(1)), int(explain_match.group(2))
    assert left_sh < 0 and right_sh > 0, "explain must gesture on both sides of body (-left, +right)"

    # 4. stop must have opposite shoulder angles
    stop_match = re.search(r'case "stop":.*?leftShoulderAngle:\s*(-?\d+).*?rightShoulderAngle:\s*(-?\d+)', content, re.DOTALL)
    assert stop_match, "stop must define shoulder angles"
    left_sh, right_sh = int(stop_match.group(1)), int(stop_match.group(2))
    assert left_sh < 0 and right_sh > 0, "stop hands must thrust forward symmetrically (-left, +right)"

