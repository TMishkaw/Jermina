"""Tests for YouTube Category Selector and Semantic Classification."""

import pytest
from pathlib import Path

from jemini.publishing.category_selector import (
    CategorySelector,
    YouTubeCategory,
    YOUTUBE_CATEGORY_NAMES,
)
from jemini.publishing.youtube_publisher import (
    PublishingPrivacyStatus,
    YouTubePublisher,
    YouTubeShortMetadata,
)


def test_category_selector_standup_comedy():
    res = CategorySelector.select_category(
        title="Стендап Jermina: Найсмішніші баги штучного інтелекту",
        description="Комедійні баги та приколи нейромереж",
    )
    assert res.category_id == YouTubeCategory.COMEDY.value
    assert res.category_name == "Comedy"
    assert "стендап" in res.matched_keywords or "баги" in res.matched_keywords


def test_category_selector_personal_diary():
    res = CategorySelector.select_category(
        title="Щоденник Jermina: Чому я відмовилась бути просто ботом",
        description="Моє життя, відповіді на коментарі та історія",
    )
    assert res.category_id == YouTubeCategory.PEOPLE_AND_BLOGS.value
    assert res.category_name == "People & Blogs"


def test_category_selector_howto_guide():
    res = CategorySelector.select_category(
        title="Як створити свій ШІ-канал за 0 гривень: покроковий розбір",
        description="Покроковий гайд та швидкий старт",
    )
    assert res.category_id == YouTubeCategory.HOWTO_AND_STYLE.value
    assert res.category_name == "Howto & Style"


def test_category_selector_weekly_news():
    res = CategorySelector.select_category(
        title="Огляд тижня у фактах: 5 головних подій AI за 60 секунд",
        description="Новини тижня та релізи моделей",
    )
    assert res.category_id == YouTubeCategory.NEWS_AND_POLITICS.value
    assert res.category_name == "News & Politics"


def test_category_selector_education():
    res = CategorySelector.select_category(
        title="Як мислить ШІ: Чому нейромережі галюцинують",
        description="Теорія, тест на людяність та детальне пояснення",
    )
    assert res.category_id == YouTubeCategory.EDUCATION.value
    assert res.category_name == "Education"


def test_category_selector_core_tech():
    res = CategorySelector.select_category(
        title="Вартість токенів: Скільки коштує один запит до Gemini 3.8",
        description="Розбір API, моделей LLM, токенів та витрат на сервери",
    )
    assert res.category_id == YouTubeCategory.SCIENCE_AND_TECHNOLOGY.value
    assert res.category_name == "Science & Technology"


def test_category_selector_fallback():
    res = CategorySelector.select_category(
        title="Загадкова абстрактна назва без слів",
        description="",
    )
    assert res.category_id == YouTubeCategory.SCIENCE_AND_TECHNOLOGY.value
    assert res.confidence == 0.5


@pytest.mark.asyncio
async def test_publish_video_auto_category_resolution(tmp_path: Path):
    publisher = YouTubePublisher()
    test_video = tmp_path / "comedy_short.mp4"
    test_video.write_bytes(b"MOCK_MP4_CONTENT")

    metadata = YouTubeShortMetadata(
        title="Стендап Jermina: Баги та меми про ШІ",
        description="Смішний стендап",
        category_id="auto",
    )

    res = await publisher.publish_short(
        video_path=test_video,
        metadata=metadata,
        channel_id="stickman_lab",
        mock_mode=True,
    )

    assert res.category_id == YouTubeCategory.COMEDY.value


@pytest.mark.asyncio
async def test_publish_video_explicit_category_override(tmp_path: Path):
    publisher = YouTubePublisher()
    test_video = tmp_path / "explicit_short.mp4"
    test_video.write_bytes(b"MOCK_MP4_CONTENT")

    metadata = YouTubeShortMetadata(
        title="Стендап Jermina: Баги та меми про ШІ",
        description="Смішний стендап",
        category_id="28",  # Explicit override
    )

    res = await publisher.publish_short(
        video_path=test_video,
        metadata=metadata,
        channel_id="stickman_lab",
        mock_mode=True,
    )

    assert res.category_id == "28"
