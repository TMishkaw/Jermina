"""Unit tests for gender agreement, pronoun consistency, and character persona."""

from jemini.core.context import ChannelProfile, ChannelRegistry
from jemini.scripting.generator import ScriptGenerator
from jemini.voice.live_voice_service import VoiceArchetype


def test_jermina_female_persona_configuration():
    """Confirms Jermina default channel is configured with female persona and Aoede voice."""
    profile = ChannelRegistry.get("stickman_lab")
    assert profile.character_name == "Джерміна"
    assert profile.gender == "female"
    assert profile.voice_name == "Aoede"


def test_script_generator_prompt_gender_enforcement():
    """Ensures prompt strictly requires feminine or masculine past-tense verbs."""
    gen = ScriptGenerator()

    # Female profile
    female_profile = ChannelProfile(
        channel_id="jermina_test",
        channel_name="Jemini Lab",
        character_name="Джерміна",
        gender="female",
        voice_name="Aoede",
        core_theme="AI coding",
    )
    prompt_female = gen._build_prompt("Тест кодингу", profile=female_profile)
    assert "ЖІНОЧИЙ РІД — ДЖЕРМІНА" in prompt_female
    assert "я пішла" in prompt_female
    assert "я створила" in prompt_female
    assert "ЗАБОРОНЕНО" in prompt_female

    # Male profile
    male_profile = ChannelProfile(
        channel_id="hacker_test",
        channel_name="Cyber Ops",
        character_name="Кібер",
        gender="male",
        voice_name="Fenrir",
        core_theme="Hacking",
    )
    prompt_male = gen._build_prompt("Тест безпеки", profile=male_profile)
    assert "ЧОЛОВІЧИЙ РІД — КІБЕР" in prompt_male
    assert "я пішов" in prompt_male
    assert "я створив" in prompt_male


def test_mock_script_female_verb_agreement():
    """Checks that generated mock script uses feminine verbs for female character."""
    gen = ScriptGenerator()
    profile = ChannelRegistry.get("stickman_lab")
    script = gen._get_mock_script("Автономні Агенти", profile=profile)

    assert script.scenes[0].directive.gender == "female"
    assert script.scenes[0].directive.archetype == VoiceArchetype.AOEDE
    # Check feminine verb ending in problem scene
    assert "я створила" in script.scenes[1].text
