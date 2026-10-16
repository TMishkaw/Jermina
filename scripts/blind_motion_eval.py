"""Blind Kinematic Motion Evaluation via Gemini Multimodal.

Renders isolated stickman poses without any textual clues, prompts, or emoji hints,
and asks Gemini Multimodal to independently describe and evaluate the action,
emotion, posture naturalness, and silhouette readability.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path

from google import genai
from google.genai import types

from jemini.core.config import settings
from jemini.validation.live_motion_auditor import IsolatedMotionRenderer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("blind_eval")


async def run_blind_motion_evaluation():
    if not settings.gemini_api_keys:
        logger.error("No Gemini API keys found in settings!")
        sys.exit(1)

    api_key = settings.gemini_api_keys[0]
    client = genai.Client(api_key=api_key)
    renderer = IsolatedMotionRenderer()

    # Define test movements to evaluate completely blindly
    test_cases = [
        {
            "id": "mystery_motion_1",
            "real_preset": "shrug",
            "frame": 30,
            "prop": "none",
            "emoji": None,
            "mouth": "talking",
            "eye": "neutral",
        },
        {
            "id": "mystery_motion_2",
            "real_preset": "heart_hands",
            "frame": 30,
            "prop": "none",
            "emoji": None,
            "mouth": "smile",
            "eye": "happy",
        },
        {
            "id": "mystery_motion_3",
            "real_preset": "point_user",
            "frame": 30,
            "prop": "none",
            "emoji": None,
            "mouth": "talking",
            "eye": "neutral",
        },
    ]

    print("\n" + "=" * 80)
    print("   СЛІПИЙ АУДИТ КІНЕМАТИКИ СТІКМЕНА ЧЕРЕЗ GEMINI MULTIMODAL")
    print("   (Жодних підказок, назв жестів чи описів моделі не передається)")
    print("=" * 80 + "\n")

    for case in test_cases:
        cid = case["id"]
        real_name = case["real_preset"]
        print(f"\n>>> [1/2] Рендеринг ізольованого кадру для {cid} (Без підказок)...")

        out_path = await renderer.render_isolated_still(
            animation=real_name,
            frame=case["frame"],
            out_filename=f"{cid}.png",
            prop=case["prop"],
            emoji=case["emoji"],
            mouth_type=case["mouth"],
            eye_type=case["eye"],
            mock_mode=False,
        )

        img_bytes = out_path.read_bytes()
        print(f"✓ Кадр успішно згенеровано: {out_path.name} ({len(img_bytes) / 1024:.1f} KB)")
        print(f">>> [2/2] Відправка в Gemini Multimodal для сліпого розпізнавання...")

        prompt = (
            "Поглянь на це зображення персонажа-стікмена на ізольованому темному фоні.\n"
            "Тобі НАВМИСНО НЕ НАДАНО жодної назви, опису чи підказки про цей рух.\n\n"
            "Дай чіткі, конкретні та чесні відповіді на такі запитання:\n"
            "1. ЩО САМЕ РОБИТЬ ПЕРСОНАЖ? Опиши дію, позу або жест, який ти бачиш.\n"
            "2. ЯКУ ЕМОЦІЮ, СТАН ЧИ МЕСЕДЖ він передає глядачеві?\n"
            "3. ОЦІНИ АНАТОМІЧНУ ПРИРОДНІСТЬ: як виглядають плечі, лікті, постава, нахил тіла? "
            "Чи немає вивернутих або зламаних суглобів?\n"
            "4. ЧИТАБЕЛЬНІСТЬ СИЛУЕТУ: наскільки швидко цей силует зчитується на екрані смартфона (9:16)?\n"
            "5. ПІДСУМКОВА ОЦІНКА: постав бал від 1 до 10 за виразність та переконливість жесту."
        )

        models_to_try = ["gemini-2.5-pro", "gemini-3.8-flash", "gemini-3.1-flash-lite"]
        response_text = None

        for model_name in models_to_try:
            for k_idx, key in enumerate(settings.gemini_api_keys):
                try:
                    c = genai.Client(api_key=key)
                    resp = c.models.generate_content(
                        model=model_name,
                        contents=[
                            types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                            prompt,
                        ],
                    )
                    if resp.text:
                        response_text = resp.text.strip()
                        print(f"✓ Успішна відповідь отримана від [{model_name}] (Ключ #{k_idx+1})")
                        break
                except Exception as exc:
                    logger.warning("Спроба з %s (ключ #%d) не вдалася: %s", model_name, k_idx + 1, exc)
            if response_text:
                break

        print("\n" + "-" * 75)
        print(f"РЕАЛЬНИЙ ПРЕСЕТ У СИСТЕМІ: [{real_name.upper()}]")
        print("ВЕРДИКТ GEMINI (СЛІПЕ РОЗПІЗНАВАННЯ):")
        print("-" * 75)
        if response_text:
            print(response_text)
        else:
            print("Усі моделі наразі тимчасово перевантажені (503).")
        print("-" * 75 + "\n")


if __name__ == "__main__":
    asyncio.run(run_blind_motion_evaluation())
