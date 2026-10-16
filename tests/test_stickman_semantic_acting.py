"""Tests for Stickman Semantic Acting and Floating Emoji Generation."""

from jemini.rendering.remotion_renderer import RemotionRenderer


def test_classify_semantic_cue_love_theme():
    # Love / Heart keywords
    anim, eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Чи може штучний інтелект відчувати любов?", fallback_idx=0
    )
    assert anim == "celebrate"
    assert eye == "happy"
    assert emoji == "💖"


def test_classify_semantic_cue_question_theme():
    # Question / Paradox
    anim, eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Чому ніхто не знає відповіді на цей парадокс?", fallback_idx=0
    )
    assert anim == "point_up"
    assert eye == "wide"
    assert emoji == "❓"


def test_classify_semantic_cue_brain_ai_theme():
    # AI / Brain / Code
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Мозок нейромережі аналізує терабайти коду", fallback_idx=0
    )
    assert anim == "point_up"
    assert emoji == "🧠"
    assert prop == "laptop"


def test_classify_semantic_cue_robot_theme():
    # Robot / Factory
    anim, _eye, _mouth, _prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Роботи вийшли на фабрики та замінюють людей", fallback_idx=0
    )
    assert anim == "walk"
    assert emoji == "🤖"


def test_classify_semantic_cue_cta_theme():
    # Call to action
    anim, _eye, _mouth, prop, emoji = RemotionRenderer._classify_semantic_cue(
        "Підписуйся на канал Jemini та пиши коментар!", fallback_idx=0
    )
    assert anim == "celebrate"
    assert emoji == "👇"
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
    assert cues[0]["emoji"] == "💖"
    assert cues[0]["animation"] == "celebrate"

    # Cue 2: Robot / AI
    assert cues[1]["emoji"] in ("🤖", "🧠", "❓")

    # Cue 3: CTA
    assert cues[2]["emoji"] == "👇"
