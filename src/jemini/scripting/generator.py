"""Script Generator for Viral 9:16 Shorts powered by Gemini 3.1 Flash Lite.

Generates high-retention 4-scene video scripts adhering to the Golden Acting Standard
and structured for parallel speech synthesis and Remotion animation.
"""

import json
import logging

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from jemini.core.config import settings
from jemini.core.context import ChannelProfile
from jemini.orchestration.parallel_pipeline import SceneScript
from jemini.rotator.rotator import APIKeyRotator
from jemini.rotator.router import TaskTier
from jemini.voice.live_voice_service import VoiceArchetype, VoiceDirective

logger = logging.getLogger(__name__)


class GeneratedShortScript(BaseModel):
    """Complete structured output of the script generation stage."""
    title: str
    hook_text: str
    scenes: list[SceneScript] = Field(default_factory=list)


class ScriptGenerator:
    """Produces structured viral scripts via gemini-3.1-flash-lite."""

    DEFAULT_MODEL = "gemini-3.1-flash-lite"

    def __init__(self, rotator: APIKeyRotator | None = None):
        self.rotator = rotator

    def _build_prompt(
        self,
        topic: str,
        profile: ChannelProfile | None = None,
        negative_rules: list[str] | None = None,
    ) -> str:
        channel_name = profile.channel_name if profile else "Jemini Stickman Lab"
        tone = profile.tone_of_voice if profile else "energetic, witty, authoritative"
        voice = profile.voice_name if profile and profile.voice_name else "Aoede"
        keywords = ", ".join(profile.niche_keywords) if profile and profile.niche_keywords else "AI, Tech"
        gender = getattr(profile, "gender", "female") if profile else "female"
        char_name = getattr(profile, "character_name", "Джерміна") if profile else "Джерміна"

        if gender == "female":
            gender_rules = (
                f"\nГРАМАТИЧНИЙ РІД ТА ПЕРСОНАЖ (ЖІНОЧИЙ РІД — {char_name.upper()}):\n"
                f"- Головна героїня ролика — {char_name} (девочка / дівчина, жіночий рід).\n"
                "- УСІ дієслова минулого часу, займенники та прикметники від першої особи 'Я' СТРОГО в ЖІНОЧОМУ роді:\n"
                "  • ПРАВИЛЬНО: «я пішла», «я створила», «я помітила», «я перевірила», «я розібралась», «я впевнена».\n"
                "  • КАТЕГОРИЧНО ЗАБОРОНЕНО писати в чоловічому роді («я пішов», «я створив», «я розібрався», «я помітив»)!\n"
                f"- Якщо у сценарії згадується персонаж у третій особі — вживай «вона», «наша {char_name}»."
            )
        else:
            gender_rules = (
                f"\nГРАМАТИЧНИЙ РІД ТА ПЕРСОНАЖ (ЧОЛОВІЧИЙ РІД — {char_name.upper()}):\n"
                f"- Ведучий ролика — {char_name} (чоловічий рід).\n"
                "- Усі дієслова від першої особи 'Я' СТРОГО в ЧОЛОВІЧОМУ роді: «я пішов», «я створив», «я перевірив», «я впевнений».\n"
                f"- Якщо у сценарії персонаж згадується у третій особі — вживай «він», «він зробив»."
            )

        rules_clause = ""
        if negative_rules:
            rules_clause = (
                "\n\nПРАВИЛА САМОНАВЧАННЯ (ВИПРАВЛЕННЯ ВІДТОКУ АУДИТОРІЇ З RETENTION FEEDBACK):\n"
                + "\n".join(f"- {r}" for r in negative_rules)
            )

        return (
            f"Ти — провідний сценарний редактор вірусних 9:16 Shorts/Reels для каналу '{channel_name}'.\n"
            f"Тема ролика: {topic}\n"
            f"Ключові нішеві акценти: {keywords}\n"
            f"Тональність: {tone}\n"
            f"Цільовий голос/архетип: {voice}\n"
            f"{gender_rules}\n\n"
            "СТРУКТУРА СЦЕНАРІЮ (РІВНО 4 СЦЕНИ, ДО 100 СЛІВ СУМАРНО):\n"
            "1. scene_01_hook (0-3 сек): Шокуюче відкриття, парадокс або провокаційне запитання. SFX: ['whoosh']\n"
            "2. scene_02_problem (3-12 сек): Біль аудиторії або несподіваний технічний факт. SFX: ['pop']\n"
            "3. scene_03_solution (12-22 сек): Розв'язка, інсайт, демонстрація сили технології. SFX: ['hit']\n"
            "4. scene_04_cta (22-30 сек): Енергійний заклик підписатися на канал. SFX: ['chime']\n\n"
            "ЗОЛОТИЙ СТАНДАРТ ОЗВУЧЕННЯ:\n"
            "- Жодних синтетичних 'ха-ха'! Використовуй ремарки емоцій, живі смішки та зітхання.\n"
            f"- Голосовий архетип: '{voice}'.\n"
            f"- Текст кожної сцени має бути до 30 слів (під безпечний ліміт Live API).{rules_clause}"
        )

    def _get_mock_script(self, topic: str, profile: ChannelProfile | None = None) -> GeneratedShortScript:
        """Returns deterministic high-quality script for offline tests."""
        voice_str = (profile.voice_name.capitalize() if profile and profile.voice_name else "Aoede")
        gender = profile.gender if profile and hasattr(profile, "gender") else "female"
        char_name = profile.character_name if profile and hasattr(profile, "character_name") else "Джерміна"
        try:
            chosen_archetype = VoiceArchetype(voice_str)
        except ValueError:
            chosen_archetype = VoiceArchetype.AOEDE if gender == "female" else VoiceArchetype.ZEPHYR

        channel_title = profile.channel_name if profile else "Jemini"

        if gender == "female":
            scene2_text = "Поки інші витрачають години на рутину, я створила систему, що вирішує це за лічені секунди."
            scene4_text = f"Тисни підписку на {channel_title}, я розкажу ще більше секретів кодингу!"
        else:
            scene2_text = "Поки інші витрачають години на рутину, сучасні автономні системи вирішують це за лічені секунди."
            scene4_text = f"Тисни підписку на {channel_title}, щоб завжди бути на крок попереду!"

        return GeneratedShortScript(
            title=f"Viral Short: {topic}",
            hook_text="СТОП! ВОНИ ЗНОВУ ЦЕ ЗРОБИЛИ?!",
            scenes=[
                SceneScript(
                    scene_id="scene_01_hook",
                    text=f"Стоп! Ти досі не знаєш як працює {topic}?!",
                    directive=VoiceDirective(
                        archetype=chosen_archetype,
                        gender=gender,
                        character_name=char_name,
                        emotion="shocked, energetic",
                    ),
                    expected_sfx=["whoosh"],
                ),
                SceneScript(
                    scene_id="scene_02_problem",
                    text=scene2_text,
                    directive=VoiceDirective(
                        archetype=chosen_archetype,
                        gender=gender,
                        character_name=char_name,
                        emotion="confident, vocal fry",
                        vocal_fry=True,
                    ),
                    expected_sfx=["pop"],
                ),
                SceneScript(
                    scene_id="scene_03_solution",
                    text=f"Канал {channel_title} розкриває секрети технологій через мультимодальні алгоритми нового покоління!",
                    directive=VoiceDirective(
                        archetype=chosen_archetype,
                        gender=gender,
                        character_name=char_name,
                        emotion="dynamic, laughing",
                    ),
                    expected_sfx=["hit"],
                ),
                SceneScript(
                    scene_id="scene_04_cta",
                    text=scene4_text,
                    directive=VoiceDirective(
                        archetype=chosen_archetype,
                        gender=gender,
                        character_name=char_name,
                        emotion="commanding, warm",
                    ),
                    expected_sfx=["chime"],
                ),
            ],
        )

    async def generate_script(
        self,
        topic: str,
        profile: ChannelProfile | None = None,
        negative_rules: list[str] | None = None,
        mock_mode: bool = False,
    ) -> GeneratedShortScript:
        """Generates structured script adhering to Pydantic contract."""
        if mock_mode or not settings.gemini_api_keys:
            logger.info("Generating mock script for topic: %s", topic)
            return self._get_mock_script(topic, profile)

        api_key = settings.gemini_api_keys[0]
        if self.rotator:
            try:
                acquired = await self.rotator.get_active_key(tier=TaskTier.ROUTINE)
                api_key = acquired.key_string
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to get key from rotator for script, fallback: %s", exc)

        client = genai.Client(api_key=api_key)
        prompt = self._build_prompt(topic, profile, negative_rules=negative_rules)

        try:
            response = await client.aio.models.generate_content(
                model=self.DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GeneratedShortScript,
                    temperature=0.7,
                ),
            )
            raw_text = response.text or "{}"
            data = json.loads(raw_text)
            return GeneratedShortScript.model_validate(data)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Script generation via API failed (%s), using robust mock script.", exc)
            return self._get_mock_script(topic, profile)
