"""Tests for Stickman Semantic Acting and Floating Emoji Generation."""

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
