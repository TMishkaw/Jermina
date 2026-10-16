"""Unit tests for MovementValidator and Autonomous A/B Convergence Engine."""

import pytest

from jemini.validation.ab_testing import MovementABTester, MovementValidator


@pytest.mark.asyncio
async def test_movement_validator_isolated_element():
    validator = MovementValidator()
    result = await validator.evaluate_element(
        element_name="heart_hands",
        intent_description="Стікмен виражає любов та ніжність, складаючи руки в серце над головою",
        element_spec={
            "leftShoulderAngle": -135,
            "leftElbowAngle": 80,
            "rightShoulderAngle": -135,
            "rightElbowAngle": 80,
            "bounce": 8,
        },
        mock_mode=True,
    )

    assert result.element_name == "heart_hands"
    assert result.is_congruent is True
    assert result.score >= 7.0
    assert len(result.strengths) > 0
    assert result.evolution_direction != ""


@pytest.mark.asyncio
async def test_ab_convergence_engine_two_consecutive_wins():
    tester = MovementABTester()
    variant_a = {
        "variant": "A",
        "description": "Стиснуті лікті біля грудей",
        "arm_angle": -60,
        "elbow_angle": 30,
    }
    variant_b = {
        "variant": "B",
        "description": "Широка арка рук над головою з виразним силуетом серця",
        "arm_angle": -135,
        "elbow_angle": 80,
    }

    result = await tester.run_ab_convergence_test(
        element_name="heart_hands",
        intent_description="Виразний жест любові у форматі 9:16 Shorts",
        variant_a=variant_a,
        variant_b=variant_b,
        consecutive_target=2,
        max_rounds=4,
        mock_mode=True,
    )

    assert result.winning_variant in ("A", "B")
    assert result.consecutive_wins >= 2
    assert result.rounds_executed >= 2
    assert len(result.rationale_history) == result.rounds_executed
    assert result.is_congruent is True

    # Ensure decisions explain WHY the variant was chosen
    for decision in result.rationale_history:
        assert decision.decision_rationale != ""
        assert decision.key_differentiator != ""
        assert decision.evolution_direction != ""

    summary = result.summarize()
    assert "AUTONOMOUS A/B CONVERGENCE RESULT" in summary
    assert "DECISION RATIONALE:" in summary
    assert "VECTOR FOR FURTHER EVOLUTION:" in summary
