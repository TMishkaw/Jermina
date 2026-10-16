import pytest

from jemini.multimodal.live_engine import UniversalLiveEngine, VisionEventType
from jemini.multimodal.voice import VoiceArchetype
from jemini.rotator.rotator import APIKeyRotator
from jemini.storage.models import KeyType


@pytest.fixture
def configured_live_engine():
    rotator = APIKeyRotator()
    rotator.register_key("live_key_alpha", key_type=KeyType.FREE)
    return UniversalLiveEngine(rotator)

@pytest.mark.asyncio
async def test_scenario_a_video_evaluation(configured_live_engine):
    report = await configured_live_engine.evaluate_video_content(
        video_id="ep16_stickman_test",
        video_bytes_or_path="output/test_video.mp4"
    )
    assert report.video_id == "ep16_stickman_test"
    assert report.overall_score >= 9.0
    assert report.hook_strength_score >= 9.0
    assert report.is_approved_for_publishing is True
    assert len(report.strengths) > 0

@pytest.mark.asyncio
async def test_scenario_b_live_stream_vision_parsing(configured_live_engine):
    dummy_frame = b"\xFF\xD8\xFF\xE0" + b"\x00" * 100
    events = await configured_live_engine.parse_live_stream_frame(
        session_id="tiktok_session_101",
        platform="tiktok",
        frame_bytes=dummy_frame
    )
    assert len(events) == 1
    event = events[0]
    assert event.event_type == VisionEventType.GIFT
    assert event.detected_item == "TikTok Rose"
    assert event.confidence > 0.9

@pytest.mark.asyncio
async def test_scenario_c_voice_tts_streaming(configured_live_engine):
    stream = configured_live_engine.synthesize_acting_voice(
        script_text="Ой, не можу... Та невже цей алгоритм нарешті запрацював?",
        voice=VoiceArchetype.ZEPHYR,
        emotion="сарказм і щирий сміх"
    )
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)

    assert len(chunks) == 3
    assert all(len(c) == 4800 for c in chunks)
