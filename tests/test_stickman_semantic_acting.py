"""Tests for Stickman Semantic Acting and Floating Emoji Generation."""

import pytest

from jemini.rendering.remotion_renderer import RemotionRenderer


def test_classify_semantic_cue_love_theme():
    # Love / Heart keywords -> heart_hands
    anim, eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Чи може штучний інтелект відчувати любов?", fallback_idx=0
    )
    assert anim == "heart_hands"
    assert eye == "happy"
    assert emoji in ("💖", "❤️", "🫶", "🥰", "💕", "❤️‍🔥")


def test_classify_semantic_cue_stop_theme():
    # Stop / Halt keywords -> stop gesture
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "СТОП! Зупинись і поглянь на цей екран!", fallback_idx=0
    )
    assert anim == "stop"
    assert prop == "stop_sign"
    assert emoji in ("🛑", "✋", "⛔", "🚨", "⚠️")


def test_classify_semantic_cue_point_user_theme():
    # You / User keywords -> point_user
    anim, _eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Ти навіть не здогадуєшся, що буде далі", fallback_idx=0
    )
    assert anim == "point_user"
    assert emoji in ("🫵", "👉", "🎯", "👤")


def test_classify_semantic_cue_watch_time_theme():
    # Time / Clock / Minutes keywords -> watch_time
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "У нас є лише кілька секунд, час спливає!", fallback_idx=0
    )
    assert anim == "watch_time"
    assert prop == "watch"
    assert emoji in ("⏰", "⏳", "⏱️", "⌛", "📅")


def test_classify_semantic_cue_question_theme():
    # Question / Paradox -> shrug
    anim, eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Чому ніхто не знає відповіді на цей парадокс?", fallback_idx=0
    )
    assert anim == "shrug"
    assert eye == "wide"
    assert emoji in ("❓", "🤔", "🧐", "🤷‍♂️", "🔍")


def test_classify_semantic_cue_brain_ai_theme():
    # AI / Brain / Code -> point_to_emoji + laptop
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Мозок нейромережі аналізує терабайти коду", fallback_idx=0
    )
    assert anim == "point_to_emoji"
    assert emoji in ("🧠", "⚡", "🔮", "💡", "🧬")
    assert prop == "laptop"


def test_classify_semantic_cue_robot_theme():
    # Robot / Factory -> walk
    anim, _eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Роботи вийшли на фабрики та замінюють людей", fallback_idx=0
    )
    assert anim == "walk"
    assert emoji in ("🤖", "🦾", "⚙️", "🏭", "🔋")


def test_classify_semantic_cue_cta_theme():
    # Call to action -> point_user + microphone
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Підписуйся на канал Jemini та пиши коментар!", fallback_idx=0
    )
    assert anim == "point_user"
    assert emoji in ("👇", "🔔", "👍", "💬", "❤️")
    assert prop == "microphone"


def test_generate_stickman_cues_with_subtitles():
    renderer = RemotionRenderer()
    subtitles = [
        {"text": "Чи може ШІ відчувати любов?", "startFrame": 0, "endFrame": 90},
        {"text": "Вчені створили тест на людяність для робота", "startFrame": 90, "endFrame": 180},
        {"text": "Підписуйся на канал та пиши думку в коментарях!", "startFrame": 180, "endFrame": 270},
    ]

    cues = renderer.generate_stickman_cues(total_frames=300, subtitles=subtitles)
    assert len(cues) >= 3

    # Cue 1: Love
    assert cues[0]["emoji"] in ("💖", "❤️", "🫶", "🥰", "💕", "❤️‍🔥")
    assert cues[0]["animation"] == "heart_hands"

    # Cue 2: Robot / AI
    assert cues[1]["emoji"] in ("🤖", "🧠", "❓", "🦾", "⚙️")

    # Cue 3: CTA
    assert cues[2]["emoji"] in ("👇", "🔔", "👍")


def test_generate_cues_strict_5_to_10_bounds():
    """Verifies that regardless of how many micro-subtitles exist, cues are bounded between 5 and 10."""
    from jemini.rendering.semantic_actor import SemanticActor

    # Simulate 50 small subtitle chunks over 900 frames (30s Short)
    subtitles = [
        {"text": f"Слово номер {i} у реченні про технології", "startFrame": i * 18, "endFrame": (i + 1) * 18}
        for i in range(50)
    ]
    cues = SemanticActor.generate_cues_for_subtitles(
        total_frames=900,
        subtitles=subtitles,
        target_count_range=(5, 10),
    )

    assert 5 <= len(cues) <= 10
    # Verify continuous coverage
    assert cues[0]["fromFrame"] == 0
    assert cues[-1]["fromFrame"] + cues[-1]["durationInFrames"] == 900


@pytest.mark.asyncio
async def test_generate_cues_with_ab_evolution(tmp_path):
    """Verifies autonomous A/B evolution for beats with uncovered topics."""
    from jemini.rendering.motion_library import MotionLibraryManager
    from jemini.rendering.semantic_actor import SemanticActor
    from jemini.validation.ab_testing import MovementABTester

    cache_file = tmp_path / "motions.json"
    remotion_cache = tmp_path / "public_motions.json"
    motion_mgr = MotionLibraryManager(cache_path=cache_file, remotion_public_cache=remotion_cache)
    ab_tester = MovementABTester()

    # Subtitles with an uncovered topic
    subtitles = [
        {"text": "Чи може ШІ відчувати любов?", "startFrame": 0, "endFrame": 150},
        {"text": "Гігантські підводні піраміди на глибині десяти тисяч метрів", "startFrame": 150, "endFrame": 450},
        {"text": "Підписуйся на канал Jermina!", "startFrame": 450, "endFrame": 750},
    ]

    cues = await SemanticActor.generate_cues_with_ab_evolution(
        total_frames=750,
        subtitles=subtitles,
        motion_library=motion_mgr,
        ab_tester=ab_tester,
        target_count_range=(5, 10),
        mock_mode=True,
    )

    assert 5 <= len(cues) <= 10
    assert cues[0]["animation"] == "heart_hands"

