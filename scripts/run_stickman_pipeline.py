"""End-to-End Autonomous Stickman Shorts Pipeline.

Orchestrates:
1. Script Generation (Gemini 3.1 Flash Lite - 500 RPD)
2. Live Voice Acting Synthesis (Gemini 3.8 Live - Unlimited RPD, 24kHz PCM)
3. Procedural SFX & Asset Retrieval (MediaAssetsHub)
4. Dynamic Remotion Configuration generation
5. Ready for local or Docker headless render
"""

import asyncio
import json
import logging
from pathlib import Path

from jemini.core.config import settings
from jemini.core.context import ChannelProfile, ContextEngine
from jemini.media.assets_hub import MediaAssetsHub
from jemini.rotator.rotator import APIKeyRotator
from jemini.storage.models import KeyType
from jemini.voice.live_voice_service import (
    GeminiLiveVoiceService,
    VoiceArchetype,
    VoiceDirective,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("stickman_pipeline")


async def main():
    logger.info("Starting Autonomous Stickman Video Pipeline...")

    # 1. Setup Context & Channel Profile
    engine = ContextEngine()
    profile = ChannelProfile(
        channel_id="stickman_ai_lab",
        channel_name="Jemini Stickman Lab",
        core_theme="AI coding, viral tech hacks, and autonomous agents",
        tone_of_voice="energetic, humorous, provocative",
        constraints=["Max 30 seconds", "Must include 3-second hook", "Strict Golden Acting Standard"],
    )
    engine.set_channel_profile(profile)
    logger.info("Cascading context layers compiled.")

    # 2. Key Rotator Setup
    rotator = APIKeyRotator()
    for key in settings.gemini_api_keys:
        rotator.register_key(key, key_type=KeyType.FREE)
    logger.info("API Key Rotator initialized with %d keys.", len(settings.gemini_api_keys))

    # 3. Voice Synthesis with Gemini 3.8 Live
    voice_service = GeminiLiveVoiceService(rotator=rotator)
    script_text = (
        "Стоп! Ти досі пишеш код вручну?! "
        "Агенти Jemini щойно розгорнули Remotion-проєкт, "
        "підключили PostgreSQL та згенерували цей ролик повністю автономно! "
        "Підписуйся та спостерігай за майбутнім!"
    )

    out_audio = Path(__file__).resolve().parent.parent / "remotion" / "public" / "voice_track.wav"
    out_audio.parent.mkdir(parents=True, exist_ok=True)

    directive = VoiceDirective(
        archetype=VoiceArchetype.ZEPHYR,
        emotion="energetic, laughing, commanding",
        vocal_fry=True,
    )

    logger.info("Synthesizing voice audio via Gemini 3.8 Live...")
    voice_result = await voice_service.synthesize(
        text_to_speak=script_text,
        output_wav_path=out_audio,
        directive=directive,
        mock_mode=False,
    )
    logger.info("Voice synthesis completed: %.2fs audio written to %s", voice_result.duration_seconds, out_audio)

    # 4. Sound Effects via MediaAssetsHub
    assets_hub = MediaAssetsHub()
    whoosh_path = assets_hub.get_or_create_sfx("whoosh_fast")
    hit_path = assets_hub.get_or_create_sfx("cinematic_hit")
    logger.info("Procedural SFX prepared: %s, %s", whoosh_path.name, hit_path.name)

    # 5. Build Remotion Dynamic Input Config
    remotion_config = {
        "id": "stickman_shorts_ep01",
        "title": "Autonomous Coding with Jemini",
        "hookText": "ТИ ДОСІ ПИШЕШ КОД ВРУЧНУ?!",
        "accentColor": "#00F0FF",
        "audioSrc": "voice_track.wav",
        "audioRms": voice_result.audio_rms_per_frame,
        "stickmanCues": [
            {"fromFrame": 0, "durationInFrames": 60, "animation": "surprised", "eyeType": "wide", "mouthType": "gasp", "prop": "none"},
            {"fromFrame": 60, "durationInFrames": 120, "animation": "talk", "eyeType": "wink", "mouthType": "talking", "prop": "microphone"},
            {"fromFrame": 180, "durationInFrames": 90, "animation": "laugh", "eyeType": "happy", "mouthType": "smile", "prop": "coffee"},
            {"fromFrame": 270, "durationInFrames": 90, "animation": "point_up", "eyeType": "neutral", "mouthType": "smile", "prop": "laptop"},
        ],
        "subtitles": voice_result.suggested_cues,
    }

    config_dest = Path(__file__).resolve().parent.parent / "remotion" / "public" / "active_pipeline_config.json"
    config_dest.write_text(json.dumps(remotion_config, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("Active Remotion pipeline configuration written to %s", config_dest)

    logger.info("✓ Pipeline execution finished successfully!")
    logger.info("To render video:")
    logger.info("  Local: cd remotion && npm run render:short")
    logger.info("  Docker: docker compose --profile render run --rm remotion")


if __name__ == "__main__":
    asyncio.run(main())
