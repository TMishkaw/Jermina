"""Voice production engine following the Golden Acting Standard (Jermina Voice Global Law).

Voices:
- Zephyr: Primary blogger voice (laughter 10/10, drama/sobbing 9/10, viral energy, dominance).
- Aoede: Velvety, deep timbre (seduction, vocal fry 8/10, lullaby/tenderness 9/10, psychopathic whisper 10/10).
- Fenrir: Brutal bass voice (rage/screaming 10/10, cyborg/robot 10/10).
- Kore: Bright, trembling timbre (timid android, child fragility).
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel

class VoiceArchetype(str, Enum):
    ZEPHYR = "Zephyr"
    AOEDE = "Aoede"
    FENRIR = "Fenrir"
    KORE = "Kore"

class ActingPromptBuilder:
    """Formats speech synthesis prompts to enforce actor embodiment rather than robotic TTS."""

    @staticmethod
    def build_acting_directive(
        script_text: str,
        voice: VoiceArchetype = VoiceArchetype.ZEPHYR,
        emotion: str = "viral blogger drive",
        include_vocal_fry: bool = False,
    ) -> str:
        guidelines = [
            f"You are embodying a live character on camera. Your assigned voice personality is '{voice.value}'.",
            f"Target emotion & delivery style: {emotion}.",
            "MANDATORY GOLDEN ACTING LAWS:",
            "1. NEVER produce synthetic 'ha-ha' or 'ah-ha'. Use organic conversational exclamations ('Пфф!..', 'Ой, не можу...'), laugh through words and breathless chuckles.",
            "2. For sadness or panic: use phonetic breath catches '(схлип)', stutter hyphens ('н-невже... б-будь ласка...'), and pitch breaks.",
            "3. For whisper or ASMR: maintain 100% full whisper mode with audible air on the microphone.",
        ]
        
        if include_vocal_fry or voice == VoiceArchetype.AOEDE:
            guidelines.append("4. Incorporate dynamic vocal fry (warm raspy breath on lower registers) with audible inhales/exhales '(видих)'.")

        guidelines.append(f"\nACT AND DELIVER IN FIRST PERSON THE FOLLOWING REPLICA:\n\"{script_text}\"")
        return "\n".join(guidelines)

class VoiceProducer:
    """Manages voice generation pipelines complying with Gemini 3.8 Live API standard."""
    
    def __init__(self, default_voice: VoiceArchetype = VoiceArchetype.ZEPHYR):
        self.default_voice = default_voice

    def prepare_voice_payload(
        self,
        text: str,
        voice: Optional[VoiceArchetype] = None,
        emotion: str = "viral drive",
    ) -> dict:
        chosen_voice = voice or self.default_voice
        directive = ActingPromptBuilder.build_acting_directive(
            script_text=text,
            voice=chosen_voice,
            emotion=emotion
        )
        return {
            "model": "gemini-3.8-live",
            "voice_name": chosen_voice.value,
            "sample_rate_hz": 24000,
            "acting_prompt": directive,
        }
