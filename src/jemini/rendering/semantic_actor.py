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
        target_count_range: tuple[int, int] = (5, 10),
    ) -> list[dict[str, Any]]:
        """Generates 5 to 10 deliberate, well-paced semantic acting cues tailored to spoken subtitles."""
        min_cues, max_cues = target_count_range
        cues: list[dict[str, Any]] = []

        if not subtitles:
            raw_beats = round(total_frames / 140) if total_frames > 0 else 6
            num_beats = max(min_cues, min(max_cues, raw_beats))
            step = total_frames / num_beats
            for i in range(num_beats):
                b_start = int(round(i * step))
                b_end = int(round((i + 1) * step)) if i < num_beats - 1 else total_frames
                acting = cls.classify_phrase("", fallback_idx=i)
                cues.append({
                    "fromFrame": b_start,
                    "durationInFrames": max(b_end - b_start, 30),
                    "animation": acting.animation,
                    "eyeType": acting.eye_type,
                    "mouthType": acting.mouth_type,
                    "prop": acting.prop,
                    "emoji": acting.emoji,
                    "customPose": acting.custom_pose,
                })
            return cues

        # Determine target number of beats
        if total_frames >= min_cues * 90:
            ideal_beats = max(min_cues, min(max_cues, round(total_frames / 140)))
        else:
            ideal_beats = max(1, min(max_cues, round(total_frames / 90)))

        m = len(subtitles)
        if m >= ideal_beats:
            buckets: list[list[dict[str, Any]]] = []
            for i in range(ideal_beats):
                start_idx = int(round(i * m / ideal_beats))
                end_idx = int(round((i + 1) * m / ideal_beats))
                if start_idx < end_idx:
                    buckets.append(subtitles[start_idx:end_idx])
        else:
            working_chunks = [
                {
                    "text": s.get("text", ""),
                    "startFrame": int(s.get("startFrame", 0)),
                    "endFrame": int(s.get("endFrame", 0)),
                }
                for s in subtitles
            ]
            while len(working_chunks) < ideal_beats:
                longest_idx = max(
                    range(len(working_chunks)),
                    key=lambda idx: working_chunks[idx]["endFrame"] - working_chunks[idx]["startFrame"],
                )
                c = working_chunks[longest_idx]
                dur = c["endFrame"] - c["startFrame"]
                if dur <= 45:
                    break
                mid = c["startFrame"] + dur // 2
                c1 = {"text": c["text"], "startFrame": c["startFrame"], "endFrame": mid}
                c2 = {"text": c["text"], "startFrame": mid, "endFrame": c["endFrame"]}
                working_chunks[longest_idx : longest_idx + 1] = [c1, c2]

            buckets = [[c] for c in working_chunks]

        current_cursor = 0
        prev_anim = None
        for i, bucket in enumerate(buckets):
            b_start = current_cursor
            raw_end = int(bucket[-1].get("endFrame", b_start + 60))
            b_end = max(b_start + 30, raw_end)
            if i == len(buckets) - 1:
                b_end = max(b_end, total_frames)
            b_dur = b_end - b_start

            bucket_text = " ".join(str(s.get("text", "")) for s in bucket).strip()
            acting = cls.classify_phrase(bucket_text, fallback_idx=i)

            if acting.animation == prev_anim and prev_anim in ("talk", "idle", "laugh", "celebrate"):
                alternatives = ["explain", "point_up", "shrug", "talk"]
                alt_anim = [a for a in alternatives if a != prev_anim][i % 3]
                acting = SemanticActingCue(
                    animation=alt_anim,
                    eye_type=acting.eye_type,
                    mouth_type=acting.mouth_type,
                    prop=acting.prop if alt_anim == "talk" else "none",
                    emoji=acting.emoji,
                    custom_pose=acting.custom_pose,
                )

            prev_anim = acting.animation
            cues.append({
                "fromFrame": b_start,
                "durationInFrames": b_dur,
                "animation": acting.animation,
                "eyeType": acting.eye_type,
                "mouthType": acting.mouth_type,
                "prop": acting.prop,
                "emoji": acting.emoji,
                "customPose": acting.custom_pose,
            })
            current_cursor = b_start + b_dur

        if current_cursor < total_frames:
            acting = cls.classify_phrase("підписуйся на канал", fallback_idx=len(cues))
            cues.append({
                "fromFrame": current_cursor,
                "durationInFrames": total_frames - current_cursor,
                "animation": acting.animation,
                "eyeType": acting.eye_type,
                "mouthType": acting.mouth_type,
                "prop": acting.prop,
                "emoji": acting.emoji,
                "customPose": acting.custom_pose,
            })

        return cues

    @classmethod
    async def generate_cues_with_ab_evolution(
        cls,
        total_frames: int,
        subtitles: list[dict[str, Any]] | None = None,
        motion_library: Any | None = None,
        ab_tester: Any | None = None,
        target_count_range: tuple[int, int] = (5, 10),
        mock_mode: bool = False,
    ) -> list[dict[str, Any]]:
        """Generates 5-10 cues with autonomous A/B evolution (2-consecutive-wins) for missing presets."""
        import logging
        logger = logging.getLogger(__name__)

        base_cues = cls.generate_cues_for_subtitles(
            total_frames=total_frames,
            subtitles=subtitles,
            target_count_range=target_count_range,
        )

        if not subtitles or not ab_tester or not motion_library:
            return base_cues

        for i, cue in enumerate(base_cues):
            b_start = cue["fromFrame"]
            b_end = b_start + cue["durationInFrames"]
            overlapping = [
                str(s.get("text", "")).strip()
                for s in subtitles
                if int(s.get("endFrame", 0)) > b_start and int(s.get("startFrame", 0)) < b_end
            ]
            beat_text = " ".join(overlapping).strip()

            if not beat_text:
                continue

            # Check if this text has a strong semantic ontology keyword match
            has_direct_match = any(
                any(kw in beat_text.lower() for kw in kws if kw != "?")
                for kws, _, _, _, _, _ in SEMANTIC_ONTOLOGY
            )

            # If no direct ontology match, check motion library or trigger A/B evolution
            if not has_direct_match:
                try:
                    existing_motion = await motion_library.find_motion_for_phrase(beat_text)
                    if existing_motion:
                        cue["animation"] = existing_motion.animation
                        cue["eyeType"] = existing_motion.eye_type
                        cue["mouthType"] = existing_motion.mouth_type
                        cue["prop"] = existing_motion.prop
                        cue["emoji"] = existing_motion.emoji
                        cue["customPose"] = existing_motion.custom_pose
                    else:
                        elem_name = f"gesture_beat_{i+1}"
                        intent = f"Виразний жест для теми: '{beat_text[:60]}'"
                        logger.info("⚡ Missing preset for beat %d ('%s'). Running A/B convergence...", i + 1, beat_text[:40])
                        ab_res = await ab_tester.run_ab_test(
                            element_name=elem_name,
                            intent_description=intent,
                            required_consecutive_wins=2,
                            mock_mode=mock_mode,
                        )
                        evolved_motion = await motion_library.register_ab_winner(ab_res)
                        cue["animation"] = evolved_motion.animation
                        cue["eyeType"] = evolved_motion.eye_type
                        cue["mouthType"] = evolved_motion.mouth_type
                        cue["prop"] = evolved_motion.prop
                        cue["emoji"] = evolved_motion.emoji
                        cue["customPose"] = evolved_motion.custom_pose
                        logger.info("✓ Evolved and applied new preset '%s' to beat %d", evolved_motion.motion_id, i + 1)
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Could not execute A/B evolution for beat %d: %s", i + 1, exc)

        return base_cues
