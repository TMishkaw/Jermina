"""Autonomous Trend Scout powered by Gemini 3.1 Flash-Lite.

Scouts viral 9:16 Shorts topics based on channel theme, target audience,
and current tech industry trends.
"""

import json
import logging

from google import genai
from google.genai import types

from jemini.core.config import settings
from jemini.core.context import ChannelProfile
from jemini.rotator.rotator import APIKeyRotator
from jemini.rotator.router import TaskTier
from jemini.scheduling.models import ScoutedTopic, ScoutedTopicList

logger = logging.getLogger(__name__)


class TrendScout:
    """Scouts high-engagement viral video ideas for autonomous channels."""

    DEFAULT_MODEL = "gemini-3.1-flash-lite"

    def __init__(self, rotator: APIKeyRotator | None = None):
        self.rotator = rotator

    def _get_mock_topics(self, profile: ChannelProfile, count: int = 3) -> ScoutedTopicList:
        """Deterministic curated topics tailored to channel profile for offline/testing."""
        niche_maps = {
            "stickman_lab": [
                ScoutedTopic(
                    title="ШІ-агенти пишуть код швидше за людей: правда чи міф?",
                    hook_angle="Покажи як агент ламає стереотипи про ручний кодинг за 3 секунди",
                    target_emotion="provocative curiosity",
                    relevance_score=9.6,
                    keywords=["#AI", "#Coding", "#Automation"],
                ),
                ScoutedTopic(
                    title="Чому Remotion замінить традиційні відеоредактори",
                    hook_angle="Порівняння 10 годин ручного монтажу з 12 секундами коду",
                    target_emotion="shocking revelation",
                    relevance_score=9.2,
                    keywords=["#Remotion", "#React", "#VideoAsCode"],
                ),
                ScoutedTopic(
                    title="Gemini 3.8 Live API: синтез живих людських емоцій",
                    hook_angle="Змусь ШІ засміятися по-справжньому без фальшивих звуків",
                    target_emotion="fascination",
                    relevance_score=9.8,
                    keywords=["#Gemini", "#LiveAPI", "#VoiceAI"],
                ),
            ],
            "cyber_matrix": [
                ScoutedTopic(
                    title="Як знайти zero-day в смарт-контракті за допомогою ШІ",
                    hook_angle="Сценарій хакерської атаки на мільйони доларів",
                    target_emotion="tactical tension",
                    relevance_score=9.7,
                    keywords=["#CyberSecurity", "#ZeroDay", "#SmartContracts"],
                ),
                ScoutedTopic(
                    title="Linux Kernel 6.x: найнебезпечніші приховані вразливості",
                    hook_angle="Один хибний системний виклик — і твій сервер захоплено",
                    target_emotion="alarm, authority",
                    relevance_score=9.3,
                    keywords=["#Linux", "#DevOps", "#Kernel"],
                ),
                ScoutedTopic(
                    title="Автономний пентестинг: як ШІ атакує захищені периметри",
                    hook_angle="Симуляція проникнення через Red Team агентів",
                    target_emotion="tactical thrill",
                    relevance_score=9.5,
                    keywords=["#RedTeam", "#PenTesting", "#Security"],
                ),
            ],
            "crypto_pulse": [
                ScoutedTopic(
                    title="Алгоритмічні торгові боти нового покоління на Python",
                    hook_angle="Як мікросекундні ордери обганяють ринок на падінні",
                    target_emotion="urgent greed/caution",
                    relevance_score=9.4,
                    keywords=["#AlgoTrading", "#Python", "#Crypto"],
                ),
                ScoutedTopic(
                    title="Крах старих блокчейнів: чому майбутнє за модульністю",
                    hook_angle="Чи витримає Ethereum наплив Layer-2 транзакцій?",
                    target_emotion="analytical intrigue",
                    relevance_score=9.1,
                    keywords=["#Web3", "#Ethereum", "#Layer2"],
                ),
            ],
            "science_genesis": [
                ScoutedTopic(
                    title="Квантова перевага досягнута: що це означає для шифрування",
                    hook_angle="Квантовий кубіт зламає RSA за секунди: що робити зараз?",
                    target_emotion="cosmic awe",
                    relevance_score=9.9,
                    keywords=["#Quantum", "#Physics", "#Cryptography"],
                ),
                ScoutedTopic(
                    title="Синтетична біологія: ДНК як носій терабайтів даних",
                    hook_angle="Збережи весь інтернет людства в одній краплі води",
                    target_emotion="visionary wonder",
                    relevance_score=9.5,
                    keywords=["#BioTech", "#DNA", "#FutureTech"],
                ),
            ],
        }

        presets = niche_maps.get(profile.channel_id, niche_maps["stickman_lab"])
        return ScoutedTopicList(topics=presets[:count])

    async def scout_topics(
        self,
        profile: ChannelProfile,
        count: int = 3,
        mock_mode: bool = False,
    ) -> ScoutedTopicList:
        """Discovers trending, viral topics adhering to the channel profile."""
        if mock_mode or not settings.gemini_api_keys:
            logger.info("Using curated trending topics for channel: %s", profile.channel_name)
            return self._get_mock_topics(profile, count=count)

        api_key = settings.gemini_api_keys[0]
        if self.rotator:
            try:
                acquired = await self.rotator.get_active_key(tier=TaskTier.ROUTINE)
                api_key = acquired.key_string
            except Exception as exc:  # noqa: BLE001
                logger.warning("Rotator key acquisition failed for scout, using fallback: %s", exc)

        client = genai.Client(api_key=api_key)
        prompt = (
            f"Ти — вірусний тренд-скаут контенту YouTube Shorts / TikTok для каналу '{profile.channel_name}'.\n"
            f"Ніша та тематика: {profile.core_theme}\n"
            f"Ключові слова: {', '.join(profile.niche_keywords)}\n"
            f"Тональність каналу: {profile.tone_of_voice}\n\n"
            f"Знайди рівно {count} найактуальніших, вірусних тем для 30-секундних вертикальних відео.\n"
            "Кожна тема повинна мати чіткий 3-секундний хук-ракурс (hook_angle), оцінку віральності (relevance_score від 1 до 10) та теги."
        )

        try:
            response = await client.aio.models.generate_content(
                model=self.DEFAULT_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ScoutedTopicList,
                    temperature=0.8,
                ),
            )
            raw = response.text or "{}"
            data = json.loads(raw)
            parsed = ScoutedTopicList.model_validate(data)
            if parsed.topics:
                return parsed
        except Exception as exc:  # noqa: BLE001
            logger.warning("Scout API query failed (%s), returning curated topics.", exc)

        return self._get_mock_topics(profile, count=count)
