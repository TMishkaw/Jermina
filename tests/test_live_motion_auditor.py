"""Unit tests for LiveMotionAuditor, IsolatedMotionCanvas, and Kinematic Symmetry."""

import pytest

from jemini.validation.live_motion_auditor import (
    IsolatedMotionRenderer,
    LiveMotionAuditor,
    MotionAuditCard,
)


@pytest.mark.asyncio
async def test_isolated_motion_renderer_mock(tmp_path):
    renderer = IsolatedMotionRenderer(remotion_dir=tmp_path)
    still_path = await renderer.render_isolated_still(
        animation="heart_hands",
        frame=30,
        mock_mode=True,
    )

    assert still_path.exists()
    assert still_path.stat().st_size > 0
    assert still_path.suffix == ".png"


@pytest.mark.asyncio
async def test_live_motion_auditor_visual_audit_mock():
    auditor = LiveMotionAuditor()
    card = await auditor.audit_preset_visual(
        preset_name="heart_hands",
        intent_description="Стікмен складає руки в серце над головою",
        prop="none",
        emoji="❤️",
        mock_mode=True,
    )

    assert isinstance(card, MotionAuditCard)
    assert card.preset_name == "heart_hands"
    assert card.is_congruent is True
    assert card.score >= 8.0
    assert card.silhouette_clarity != ""
    assert card.kinematic_naturalness != ""
    assert card.semantic_accuracy != ""
    assert len(card.strengths) > 0


@pytest.mark.asyncio
async def test_live_motion_auditor_visual_ab_convergence():
    auditor = LiveMotionAuditor()

    # Variant A has inward overlapping arm angles (defective)
    variant_a = {
        "leftShoulderAngle": -135,
        "leftElbowAngle": 70,
        "rightShoulderAngle": -135,  # overlapping to the left side
        "rightElbowAngle": 70,
    }

    # Variant B has correct symmetrical outward arch
    variant_b = {
        "leftShoulderAngle": -145,
        "leftElbowAngle": -70,
        "rightShoulderAngle": 145,
        "rightElbowAngle": 70,
    }

    result = await auditor.run_visual_ab_testing(
        preset_name="heart_hands",
        intent_description="Виразне симетричне серце руками над головою без перекриття кінцівок",
        variant_a_pose=variant_a,
        variant_b_pose=variant_b,
        consecutive_target=2,
        max_rounds=4,
        mock_mode=True,
    )

    assert result.winning_variant in ("A", "B")
    assert result.consecutive_wins >= 2
    assert result.rounds_executed >= 2
    assert result.is_congruent is True
    assert len(result.rationale_history) == result.rounds_executed

    # Ensure detailed explainability exists for every round
    for dec in result.rationale_history:
        assert dec.decision_rationale != ""
        assert dec.key_differentiator != ""
        assert dec.evolution_direction != ""


@pytest.mark.asyncio
async def test_live_motion_auditor_catalog_audit_mock():
    auditor = LiveMotionAuditor()
    cards = await auditor.audit_core_motion_catalog(mock_mode=True)

    assert len(cards) == 8
    presets_audited = {c.preset_name for c in cards}
    assert "heart_hands" in presets_audited
    assert "stop" in presets_audited
    assert "point_user" in presets_audited
    assert "shrug" in presets_audited
    assert "explain" in presets_audited
    assert "celebrate" in presets_audited

    for c in cards:
        assert c.score >= 7.0
        assert c.is_congruent is True
