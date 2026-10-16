"""Unit tests for MotionLibraryManager and dynamic motion evolution."""

import pytest

from jemini.rendering.motion_library import MotionLibraryManager
from jemini.rendering.semantic_actor import SEMANTIC_ONTOLOGY
from jemini.validation.ab_testing import ABRoundDecision, ABTestConvergenceResult


@pytest.mark.asyncio
async def test_motion_library_seed_and_cache(tmp_path):
    cache_file = tmp_path / "motions.json"
    remotion_cache = tmp_path / "public_motions.json"

    manager = MotionLibraryManager(cache_path=cache_file, remotion_public_cache=remotion_cache)
    count = await manager.seed_core_ontology(SEMANTIC_ONTOLOGY[:5])

    assert count >= 5
    assert cache_file.exists()
    assert remotion_cache.exists()

    # Verify retrieval
    motion = await manager.find_motion_for_phrase("Чи може ШІ відчувати любов?")
    assert motion is not None
    assert motion.animation in ("heart_hands", "celebrate")


@pytest.mark.asyncio
async def test_motion_library_register_ab_winner(tmp_path):
    cache_file = tmp_path / "motions.json"
    remotion_cache = tmp_path / "public_motions.json"

    manager = MotionLibraryManager(cache_path=cache_file, remotion_public_cache=remotion_cache)

    ab_result = ABTestConvergenceResult(
        element_name="super_celebrate",
        intent_description="Святковий стрибок із золотими зірками",
        winning_variant="B",
        rounds_executed=2,
        consecutive_wins=2,
        rationale_history=[
            ABRoundDecision(
                round_number=1,
                chosen_variant="B",
                decision_rationale="Виразніший силует",
                variant_a_critique="",
                variant_b_critique="",
                key_differentiator="Ширина",
                evolution_direction="Додати посмішку",
            )
        ],
        winning_spec={
            "animation": "celebrate",
            "eye_type": "wink",
            "mouth_type": "smile",
            "prop": "microphone",
            "emoji": "🌟",
            "custom_pose": {"headTilt": -12, "torsoAngle": 5},
        },
        evolution_direction="Додати мікро-зум",
        is_congruent=True,
    )

    registered = await manager.register_ab_winner(ab_result)
    assert registered.motion_id == "super_celebrate_evolved"
    assert registered.emoji == "🌟"
    assert registered.custom_pose == {"headTilt": -12, "torsoAngle": 5}

    # Verify retrieved by name
    found = await manager.find_motion_for_phrase("super_celebrate")
    assert found is not None
    assert found.motion_id == "super_celebrate_evolved"
