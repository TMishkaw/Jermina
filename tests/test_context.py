import pytest
from jemini.core.context import ContextEngine, ContextLayer, ContextLayerType, ChannelProfile

def test_context_engine_layer_compilation():
    engine = ContextEngine()
    
    domain_layer = ContextLayer(
        layer_type=ContextLayerType.DOMAIN,
        name="scriptwriting",
        content="Always open with an explosive 3-second hook."
    )
    engine.register_domain_layer(domain_layer)
    
    profile = ChannelProfile(
        channel_id="ch_test",
        channel_name="Stickman Lab",
        core_theme="AI Stickman animations",
        tone_of_voice="ironic, energetic",
        constraints=["no swearing"]
    )
    engine.set_channel_profile(profile)
    
    compiled = engine.compile_system_instruction(domain_name="scriptwriting")
    
    assert "LAYER 1: CORE ENGINE INVARIANTS" in compiled
    assert "LAYER 2: DOMAIN KNOWLEDGE (scriptwriting)" in compiled
    assert "Always open with an explosive 3-second hook." in compiled
    assert "LAYER 3: CHANNEL INSTANCE CONTEXT" in compiled
    assert "Channel: Stickman Lab" in compiled
