"""Unit tests for Multi-Channel Profiles and ChannelRegistry."""

from jemini.core.context import ChannelProfile, ChannelRegistry


def test_channel_registry_presets():
    channels = ChannelRegistry.list_channels()
    assert len(channels) >= 4
    
    ids = [c.channel_id for c in channels]
    assert "stickman_lab" in ids
    assert "cyber_matrix" in ids
    assert "crypto_pulse" in ids
    assert "science_genesis" in ids

    cyber = ChannelRegistry.get("cyber_matrix")
    assert cyber.accent_color == "#00FF66"
    assert cyber.voice_name == "Fenrir"
    assert "ZeroDay" in cyber.niche_keywords


def test_channel_registry_fallback():
    # Unknown channel ID must fall back to stickman_lab safely
    fallback = ChannelRegistry.get("non_existent_channel_xyz")
    assert fallback.channel_id == "stickman_lab"
    assert fallback.accent_color == "#00F0FF"


def test_channel_registry_custom_registration():
    custom = ChannelProfile(
        channel_id="bio_hacker",
        channel_name="BioHacker Intelligence",
        core_theme="Longevity, CRISPR gene editing, and bio-optimization",
        tone_of_voice="scientific, urgent, cutting-edge",
        accent_color="#FF0077",
        voice_name="Kore",
        niche_keywords=["CRISPR", "Longevity", "BioHacking"],
    )
    ChannelRegistry.register(custom)

    retrieved = ChannelRegistry.get("bio_hacker")
    assert retrieved.channel_id == "bio_hacker"
    assert retrieved.accent_color == "#FF0077"
    assert retrieved.voice_name == "Kore"
