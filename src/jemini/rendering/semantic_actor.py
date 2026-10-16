"""Semantic Acting and Kinetic Gesture Engine for Stickman Animations.

Maps spoken Ukrainian speech and subtitles to precise physical gestures, props,
and visual contextual emojis from an extensive lexical ontology.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SemanticActingCue:
    """Actionable kinematic directing cue for a single speech segment."""
    animation: str
    eye_type: str
    mouth_type: str
    prop: str
    emoji: str | None
    custom_pose: dict[str, Any] | None = None


# Lexical semantic rule mapping: (keywords/stems, animation, eye, mouth, prop, emojis)
SEMANTIC_ONTOLOGY: list[tuple[list[str], str, str, str, str, list[str]]] = [
    # 1. STOP / ATTENTION / WAIT / HALT
    (
        [
            "стоп", "стій", "зупинись", "зачекай", "постривай", "увага", "обережно",
            "небезпек", "гальмуй", "пауза", "заборонен", "не поспішай", "стійте",
        ],
        "stop", "wide", "gasp", "stop_sign", ["🛑", "✋", "⛔", "🚨", "⚠️"],
    ),

    # 2. LOVE / HEART / FEELINGS / EMOTIONS / SOUL
    (
        [
            "любов", "коханн", "серц", "почутт", "відчува", "душ", "любит", "емоці",
            "теплот", "ніжн", "кохат", "закохан", "серденьк", "пристраст", "симпаті",
        ],
        "heart_hands", "happy", "smile", "heart", ["💖", "❤️", "🫶", "🥰", "💕", "❤️‍🔥"],
    ),

    # 3. YOU / USER / VIEWER / AUDIENCE (Addressing the audience directly)
    (
        [
            "ти", "тобі", "твоє", "твої", "твоя", "твій",
            "ви", "вам", "вас", "ваше", "ваші", "глядач", "користувач", "людино",
        ],
        "point_user", "wink", "smile", "none", ["🫵", "👉", "🎯", "👤"],
    ),

    # 4. TIME / CLOCK / HOURS / MINUTES / SPEED / DURATION
    (
        [
            "годин", "хвилин", "секунд", "час", "годинник", "встигнут", "запізн",
            "швидк", "день", "тиждень", "рік", "вічност", "таймер", "ранку", "вечора",
        ],
        "watch_time", "neutral", "talking", "watch", ["⏰", "⏳", "⏱️", "⌛", "📅"],
    ),

    # 5. PARADOX / QUESTION / MYSTERY / WHY / HOW (Doubt & Investigation)
    (
        [
            "чи може", "чи зможе", "чому", "як", "якщо", "що", "хто", "куди",
            "навіщо", "парадокс", "загадк", "таємниц", "секрет", "справді", "невже",
            "питання", "запитує", "сумнів", "невідом", "?",
        ],
        "shrug", "wide", "gasp", "none", ["❓", "🤔", "🧐", "🤷‍♂️", "🔍"],
    ),

    # 6. AI / NEURAL NETS / BRAIN / INTELLIGENCE / GEMINI / LLM / THINKING
    (
        [
            "штучн", "інтелект", "ші", "ai", "нейромереж", "мозок", "розум",
            "мислит", "алгоритм", "модел", "gemini", "gpt", "llm", "агент",
            "нейрон", "промпт", "тест на людяність", "тюрінг",
        ],
        "point_to_emoji", "neutral", "talking", "laptop", ["🧠", "⚡", "🔮", "💡", "🧬"],
    ),

    # 7. CODE / PROGRAMMING / DEVELOPER / BUG / SERVERS / REPO
    (
        [
            "код", "програміст", "розробник", "девелопер", "баг", "сервер", "api",
            "репозиторій", "python", "скрипт", "архітектур", "компіляц", "база даних",
        ],
        "point_to_emoji", "neutral", "talking", "laptop", ["💻", "👾", "🖥️", "🐞", "⌨️"],
    ),

    # 8. ROBOT / CYBORG / HARDWARE / FACTORY / MACHINE
    (
        [
            "робот", "машин", "бот", "кіборг", "заліз", "процесор", "двійник",
            "завод", "індустрі", "деталь", "чип", "механізм", "андроїд",
        ],
        "walk", "neutral", "talking", "none", ["🤖", "🦾", "⚙️", "🏭", "🔋"],
    ),

    # 9. SHOCK / BLOW MIND / CATASTROPHE / CRISIS / EXPLOSION
    (
        [
            "шок", "криз", "катастроф", "вибух", "неймовірн", "жах", "божевілл",
            "розвалює", "крах", "шок-контент", "панік", "капець",
        ],
        "shocked", "wide", "gasp", "none", ["🤯", "😱", "💥", "🧨", "🌋"],
    ),

    # 10. MONEY / CASH / TOKENS / COST / PROFIT / PRICE / FREE
    (
        [
            "грош", "долар", "гривн", "токен", "цін", "вартіст", "безкоштовн",
            "0 грн", "0$", "заробіт", "багат", "мільйон", "бюджет", "капітал", "прибут",
        ],
        "celebrate", "wink", "smile", "none", ["💸", "💰", "🤑", "💎", "💳"],
    ),

    # 11. HUMOR / JOKE / LAUGH / COFFEE / CHILL / IRONY
    (
        [
            "смішн", "жарт", "ха-ха", "посміш", "пфф", "кав", "відпочин", "мем",
            "іроні", "весел", "прикол", "анекдот", "чай",
        ],
        "laugh", "happy", "smile", "coffee", ["😂", "🤣", "☕", "💀", "😏"],
    ),

    # 12. VIRAL / FIRE / WIN / TOP / RECORD / BREAKTHROUGH
    (
        [
            "топ", "вогонь", "розрив", "прорив", "перемог", "рекорд", "лідер",
            "кращ", "номер один", "найкращ", "бомб", "вірусн", "хайп",
        ],
        "celebrate", "happy", "smile", "none", ["🔥", "🚀", "🏆", "🥇", "⭐"],
    ),

    # 13. CALL TO ACTION / SUBSCRIBE / LIKE / BELL / FOLLOW / COMMENT
    (
        [
            "підпис", "канал", "коментар", "тисн", "лайк", "дзвіноч", "дивіть",
            "посиланн", "підпишіться", "тисни лайк", "натискай", "долучайся",
        ],
        "point_user", "wink", "smile", "microphone", ["👇", "🔔", "👍", "💬", "❤️"],
    ),

    # 14. TRUTH / LIE / DETECTIVE / SECRET / FRAUD
    (
        [
            "правд", "брехн", "обман", "детектив", "розслідуванн", "фейк", "істин",
            "пастк", "маніпуляц", "шахрай",
        ],
        "shrug", "wide", "neutral", "none", ["🕵️", "🤥", "🔍", "👀"],
    ),

    # 15. QUANTUM / PHYSICS / COSMOS / SINGULARITY
    (
        [
            "квантов", "фізик", "космос", "сингулярност", "всесвіт", "простір",
            "галактик", "матері", "енергі",
        ],
        "point_to_emoji", "wide", "gasp", "none", ["⚛️", "🌌", "🪐", "✨"],
    ),
]


class SemanticActor:
    """Intelligent semantic acting director for Stickman animations."""

    @classmethod
    def classify_phrase(cls, text: str, fallback_idx: int = 0) -> SemanticActingCue:
        """Classifies spoken text and returns a rich kinematic acting cue."""
        lower = text.lower().strip()

        for keywords, anim, eye, mouth, prop, emojis in SEMANTIC_ONTOLOGY:
            for kw in keywords:
                if kw == "?":
                    if "?" in lower:
                        emoji_choice = emojis[0] if emojis else None
                        return SemanticActingCue(
                            animation=anim,
                            eye_type=eye,
                            mouth_type=mouth,
                            prop=prop,
                            emoji=emoji_choice,
                        )
                    continue

                clean_kw = kw.strip()
                if not clean_kw:
                    continue

                if len(clean_kw) <= 3:
                    pattern = rf"(?:\b|[^\wа-яіїєґ]){re.escape(clean_kw)}(?:\b|[^\wа-яіїєґ])"
                    if re.search(pattern, lower, re.IGNORECASE):
                        emoji_choice = emojis[0] if emojis else None
                        return SemanticActingCue(
                            animation=anim,
                            eye_type=eye,
                            mouth_type=mouth,
                            prop=prop,
                            emoji=emoji_choice,
                        )
                elif clean_kw in lower:
                    emoji_choice = emojis[0] if emojis else None
                    return SemanticActingCue(
                        animation=anim,
                        eye_type=eye,
                        mouth_type=mouth,
                        prop=prop,
                        emoji=emoji_choice,
                    )

        # Dynamic fallback rotation for non-matching conversational cadence
        conversational_cadence = [
            ("surprised", "wide", "gasp", "none", "🤯"),
            ("talk", "neutral", "talking", "microphone", "💡"),
            ("point_up", "wink", "smile", "none", "⚡"),
            ("laugh", "happy", "smile", "coffee", "😂"),
            ("celebrate", "happy", "smile", "none", "🚀"),
        ]
        anim, eye, mouth, prop, emoji = conversational_cadence[fallback_idx % len(conversational_cadence)]
        return SemanticActingCue(
            animation=anim,
            eye_type=eye,
            mouth_type=mouth,
            prop=prop,
            emoji=emoji,
        )

    @classmethod
    def generate_cues_for_subtitles(
        cls,
        total_frames: int,
        subtitles: list[dict[str, Any]] | None = None,
    ) -> list[dict[str, Any]]:
        """Transforms subtitles into a continuous, frame-accurate kinematic acting cue timeline."""
        cues: list[dict[str, Any]] = []

        if subtitles:
            current_cursor = 0
            for idx, sub in enumerate(subtitles):
                s_start = int(sub.get("startFrame", current_cursor))
                s_end = int(sub.get("endFrame", s_start + 60))
                s_text = str(sub.get("text", ""))

                # Fill any pause/gap before this subtitle
                if s_start > current_cursor:
                    gap_dur = s_start - current_cursor
                    acting = cls.classify_phrase("", idx)
                    cues.append({
                        "fromFrame": current_cursor,
                        "durationInFrames": gap_dur,
                        "animation": acting.animation,
                        "eyeType": acting.eye_type,
                        "mouthType": acting.mouth_type,
                        "prop": acting.prop,
                        "emoji": acting.emoji,
                        "customPose": acting.custom_pose,
                    })
                    current_cursor = s_start

                # Add semantic cue for the spoken subtitle
                sub_dur = max(s_end - s_start, 30)
                acting = cls.classify_phrase(s_text, idx)
                cues.append({
                    "fromFrame": s_start,
                    "durationInFrames": sub_dur,
                    "animation": acting.animation,
                    "eyeType": acting.eye_type,
                    "mouthType": acting.mouth_type,
                    "prop": acting.prop,
                    "emoji": acting.emoji,
                    "customPose": acting.custom_pose,
                })
                current_cursor = s_start + sub_dur

            # Fill remaining frames if audio continues past last subtitle
            if current_cursor < total_frames:
                rem_dur = total_frames - current_cursor
                acting = cls.classify_phrase("підпишись на канал", len(subtitles))
                cues.append({
                    "fromFrame": current_cursor,
                    "durationInFrames": rem_dur,
                    "animation": acting.animation,
                    "eyeType": acting.eye_type,
                    "mouthType": acting.mouth_type,
                    "prop": acting.prop,
                    "emoji": acting.emoji,
                    "customPose": acting.custom_pose,
                })
            return cues

        # Default rotation if no subtitles provided
        current_frame = 0
        step_duration = 60
        idx = 0
        while current_frame < total_frames:
            dur = min(step_duration, total_frames - current_frame)
            acting = cls.classify_phrase("", idx)
            cues.append({
                "fromFrame": current_frame,
                "durationInFrames": dur,
                "animation": acting.animation,
                "eyeType": acting.eye_type,
                "mouthType": acting.mouth_type,
                "prop": acting.prop,
                "emoji": acting.emoji,
                "customPose": acting.custom_pose,
            })
            current_frame += dur
            idx += 1

        return cues
