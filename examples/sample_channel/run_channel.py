"""Sample channel runner demonstrating independent channel usage of Jemini core."""

import asyncio
from pathlib import Path
from jemini.core.context import ContextEngine, ChannelProfile
from jemini.multimodal.voice import VoiceProducer, VoiceArchetype

try:
    import yaml
    def load_profile(path: Path) -> dict:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
except ImportError:
    def load_profile(path: Path) -> dict:
        # Fallback profile dictionary
        return {
            "channel_id": "jermina_official",
            "channel_name": "Jermina Voice Chronicles",
            "core_theme": "Гумористичні та кібернетичні скетчі про штучний інтелект",
            "tone_of_voice": "viral blogger drive, сарказм, жива емоційність",
            "target_platforms": ["youtube", "tiktok"],
            "constraints": ["Ніякого плоского синтезу мовлення", "Суворе дотримання Golden Acting Standard"],
            "custom_settings": {"preferred_voice": "Zephyr", "hook_duration_seconds": 3}
        }

async def main():
    profile_path = Path(__file__).parent / "channel_profile.yaml"
    data = load_profile(profile_path)

    profile = ChannelProfile(**data)
    engine = ContextEngine()
    engine.set_channel_profile(profile)

    system_instruction = engine.compile_system_instruction()
    print("=== Compiled Channel Prompt ===")
    print(system_instruction[:300] + "...\n")

    producer = VoiceProducer(default_voice=VoiceArchetype.ZEPHYR)
    voice_directive = producer.prepare_voice_payload(
        text="Пфф!.. Та ви серйозно думали, що нейронка не вміє сміятися?",
        emotion="сміх крізь слова та легкий подив"
    )
    print("=== Voice Directive Payload ===")
    print(voice_directive["acting_prompt"])

if __name__ == "__main__":
    asyncio.run(main())
