"""YouTube Video Category Selector and Semantic Classifier.

Determines the most accurate YouTube Category ID for videos based on topic,
script keywords, tone, and channel identity to maximize algorithmic recommendation.
"""

from enum import Enum
import re
from typing import Any
from pydantic import BaseModel, Field


class YouTubeCategory(str, Enum):
    """Official YouTube Video Categories (Region UA / Global)."""
    FILM_AND_ANIMATION = "1"
    AUTOS_AND_VEHICLES = "2"
    MUSIC = "10"
    PETS_AND_ANIMALS = "15"
    SPORTS = "17"
    SHORT_MOVIES = "18"
    TRAVEL_AND_EVENTS = "19"
    GAMING = "20"
    VIDEOBLOGGING = "21"
    PEOPLE_AND_BLOGS = "22"
    COMEDY = "23"
    ENTERTAINMENT = "24"
    NEWS_AND_POLITICS = "25"
    HOWTO_AND_STYLE = "26"
    EDUCATION = "27"
    SCIENCE_AND_TECHNOLOGY = "28"
    DOCUMENTARY = "35"


YOUTUBE_CATEGORY_NAMES: dict[str, str] = {
    "1": "Film & Animation",
    "2": "Autos & Vehicles",
    "10": "Music",
    "15": "Pets & Animals",
    "17": "Sports",
    "18": "Short Movies",
    "19": "Travel & Events",
    "20": "Gaming",
    "21": "Videoblogging",
    "22": "People & Blogs",
    "23": "Comedy",
    "24": "Entertainment",
    "25": "News & Politics",
    "26": "Howto & Style",
    "27": "Education",
    "28": "Science & Technology",
    "35": "Documentary",
}


class CategoryMatchResult(BaseModel):
    """Result of YouTube category classification."""
    category_id: str
    category_name: str
    confidence: float = Field(ge=0.0, le=1.0)
    matched_keywords: list[str] = Field(default_factory=list)
    reasoning: str = ""


# Semantic rule dictionary with weights
# (category_id, keywords, weight)
CATEGORY_ONTOLOGY: list[tuple[YouTubeCategory, list[str], float]] = [
    # 1. Comedy (23) - High priority triggers
    (
        YouTubeCategory.COMEDY,
        [
            "стендап", "standup", "гумор", "жарт", "мем", "смішн", "прикол", "баги",
            "фейл", "іронія", "сатира", "ржака", "пфф", "ой не можу", "сміх", "comedy"
        ],
        1.5,
    ),
    # 2. People & Blogs (22) - Personal stories, diary, community Q&A
    (
        YouTubeCategory.PEOPLE_AND_BLOGS,
        [
            "щоденник", "щоденник jermina", "відповіді на коментарі", "відповідає хейтерам",
            "про себе", "чому я відмовилась", "чому я перестав", "моє життя", "хто я",
            "особисте", "глядач", "хейтер", "підписник"
        ],
        1.4,
    ),
    # 3. Howto & Style (26) - Step-by-step guides, tooling, 0 UAH setup
    (
        YouTubeCategory.HOWTO_AND_STYLE,
        [
            "як створити", "покроковий", "гайд", "туторіал", "як зробити", "налаштуван",
            "0 гривень", "0 грн", "швидкий старт", "інструменти", "топ-3 інструменти",
            "збереже вам", "лайфхак", "manual", "guide", "setup"
        ],
        1.3,
    ),
    # 4. Education (27) - Explanations, how it thinks, deep dives, theory
    (
        YouTubeCategory.EDUCATION,
        [
            "як мислить", "чому нейромережі", "тест на людяність", "тест тюрінга",
            "як працює", "теорія", "що таке", "пояснення", "навчання", "розбір",
            "чому саме", "чи є свідомість", "детально про", "аналітика", "правила"
        ],
        1.2,
    ),
    # 5. News & Politics (25) - Weekly roundups, legal, industry facts
    (
        YouTubeCategory.NEWS_AND_POLITICS,
        [
            "огляд тижня", "новини", "події", "головних подій", "фактах", "за 60 секунд",
            "реліз", "анонс", "злив", "скандал", "закон", "заборона", "новина", "news"
        ],
        1.3,
    ),
    # 6. Entertainment (24) - Crash-tests, paradoxes, challenges, drama
    (
        YouTubeCategory.ENTERTAINMENT,
        [
            "краш-тест", "парадокс", "гострий парадокс", "битва", "проти", "vs", "versus",
            "людина vs", "челендж", "шоу", "експеримент", "чи відчуває", "відчувати любов",
            "чи може ші", "інтрига", "провокація", "вірусна гіпотеза", "розслідування",
            "детектив", "ai-детектив", "змова"
        ],
        1.1,
    ),
    # 7. Science & Technology (28) - Core AI, coding, infrastructure, quantum, security
    (
        YouTubeCategory.SCIENCE_AND_TECHNOLOGY,
        [
            "штучний інтелект", "ші", "ai", "нейромереж", "робот", "модел", "кодер",
            "програміст", "програмісти 2026", "синтаксис", "токен", "вартість токенів",
            "gemini", "gemini 3.8", "llm", "gpt", "квантовий ші", "кванти", "сингулярність",
            "кібербезпека", "зламати", "промпт", "api", "код", "алгоритм", "технолог",
            "сервер", "суперінтелект", "agi", "софт", "python", "benchmark"
        ],
        1.0,
    ),
    # 8. Film & Animation (1) - 3D procedural scenes, CGI, kinematics
    (
        YouTubeCategory.FILM_AND_ANIMATION,
        [
            "анімація", "animation", "blender", "3d", "кінематика", "мультфільм",
            "короткометражка", "cgi", "render"
        ],
        1.2,
    ),
]


class CategorySelector:
    """Semantic YouTube Video Category Classifier."""

    @classmethod
    def select_category(
        cls,
        title: str,
        description: str = "",
        tags: list[str] | None = None,
        default_category: str = YouTubeCategory.SCIENCE_AND_TECHNOLOGY.value,
    ) -> CategoryMatchResult:
        """Classifies video text into the most optimal YouTube Category ID."""
        tags = tags or []
        full_text = f"{title} {description} {' '.join(tags)}".lower()

        scores: dict[YouTubeCategory, float] = {}
        matched_map: dict[YouTubeCategory, list[str]] = {}

        for category, keywords, weight in CATEGORY_ONTOLOGY:
            current_matches: list[str] = []
            score = 0.0

            for kw in keywords:
                # Use word boundary or exact substring check
                if " " in kw:
                    if kw in full_text:
                        score += 2.0 * weight
                        current_matches.append(kw)
                else:
                    pattern = rf"\b{re.escape(kw)}"
                    matches = re.findall(pattern, full_text)
                    if matches:
                        score += len(matches) * weight
                        current_matches.append(kw)

            if score > 0:
                scores[category] = score
                matched_map[category] = current_matches

        if not scores:
            return CategoryMatchResult(
                category_id=default_category,
                category_name=YOUTUBE_CATEGORY_NAMES.get(default_category, "Science & Technology"),
                confidence=0.5,
                matched_keywords=[],
                reasoning=f"No strong semantic category trigger found. Defaulting to channel primary category ({default_category}).",
            )

        # Pick highest scoring category
        best_category = max(scores, key=scores.get)
        max_score = scores[best_category]
        total_score = sum(scores.values())
        confidence = min(0.99, round(max_score / total_score, 2)) if total_score > 0 else 0.5

        matched_kws = list(dict.fromkeys(matched_map[best_category]))[:6]
        cat_id = best_category.value
        cat_name = YOUTUBE_CATEGORY_NAMES.get(cat_id, "Unknown")

        reasoning = (
            f"Classified as '{cat_name}' (ID {cat_id}) with score {max_score:.1f}. "
            f"Matched triggers: {', '.join(matched_kws)}"
        )

        return CategoryMatchResult(
            category_id=cat_id,
            category_name=cat_name,
            confidence=confidence,
            matched_keywords=matched_kws,
            reasoning=reasoning,
        )
