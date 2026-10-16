---
name: jermina-brain-memory
description: Rules, governance, and modular memory loading protocols for the JERMINA MySQL Brain memory (`jermina_db.brain`). Defines strict versioning (v2.3.0+), anti-pollution standards, and domain-targeted retrieval to eliminate LLM context noise and unauthorized version bumps.
---

# JERMINA Brain Memory Governance & Modular Loading Protocol

Цей стандарт є обов'язковим для ВСІХ субагентів, скриптів та оркестраторів студії JERMINA.

---

## 1. Фундаментальні закони пам'яті (SSOT Brain Laws)

### Закон 1: Суворе версіонування (Strict Versioning Law)
- **Поточна еталонна версія ядра**: `v2.3.0`.
- **Заборона довільного підвищення версій**: Жоден субагент, скрипт чи виконавець не має права самостійно підвищувати версію домену в таблиці `brain` або створювати нові мінорні/мажорні версії.
- **Право версіонування**: Тільки **`Germina (AI Core)` (`who_id = 2`)** або **`AI Brain Main` (`who_id = 17`)** мають повноваження змінювати `brain.version`.
- Кожна зміна версії зобов'язана фіксуватися в таблиці `brain_versions` із заповненням полів: `brain_id`, `version`, `change_summary`, `who_id`, `created_at`.

### Закон 2: Модульне завантаження (Modular Memory Loading — No Context Pollution)
- **Категорична заборона**: Ніколи не вивантажувати всі 10 доменів таблиці `brain` у контекстне вікно моделі одночасно. Це викликає галюцинації, шум та перевитрату токенів.
- **Цільове завантаження за роллю**: Кожен агент завантажує ВИКЛЮЧНО той домен, який безпосередньо стосується його поточного завдання:

| Роль агента | `who_id` | Необхідний домен `brain.section` | Опис домену |
|---|---|---|---|
| **AI Brain Main** | `17` | `core_system_architecture`, `multi_agent_hierarchy` | Загальна топологія, делегування, системні правила |
| **AI Video Director** | `12` | `creative_direction_and_style`, `vfx_and_animation_specs` | Візуальний стиль, монтаж, темпоритм |
| **AI Voice Director** | `15` | `voice_and_audio_standards` | Gemini 3.8 Live API, Zephyr/Aoede/Fenrir, 24kHz |
| **AI VFX Developer** | `14` | `vfx_and_animation_specs` | Remotion, Blender, Three.js, HUD-графіка |
| **AI Community / SMM** | `11` | `social_media_and_distribution` | YouTube Shorts, метадані, 3-сек хуки, розклад |
| **AI Content Editor** | `18` | `news_and_content_strategy` | Новини, дедуплікація, формування дайджестів |
| **AI Statistician** | `16` | `studio_governance_and_metrics` | KPI, аналітика охоплень, звіти ітерацій |
| **AI Core & Dev** | `2` | `database_and_persistence`, `operational_memory_and_incidents` | Схеми БД, міграції, верифіковані інциденти |

### Закон 3: Закон проти шуму та сміття (Zero-Noise Anti-Pollution Law)
- Таблиця `operational_memory_and_incidents` призначена **ВИКЛЮЧНО** для:
  1. Верифікованих архітектурних рішень (Architectural Decision Records).
  2. Виправлених критичних багів (Bug Postmortems із рішенням).
  3. Офіційних регламентів дій.
- **Суворо заборонено записувати**:
  - Повні транскрипти діалогів чату або сесій.
  - Сирі виклики інструментів, тимчасові JSON-дампи та прогрес-логи.
  - Повторювані записи про кожну дію.
- Для технічних логів використовується таблиця `log` та `log_details`, а не `brain`!

---

## 2. Програмний API для взаємодії з Мозком (`BrainService`)

Для читання та запису завжди використовуйте сервіс [`src/brain/brain_service.py`](file:///D:/JERMINA/src/brain/brain_service.py):

```python
from src.brain.brain_service import BrainService

brain = BrainService(default_who_id=17)

# 1. Точкове модульне читання (БЕЗ шуму всього мозку)
voice_domain = brain.get_section("voice_and_audio_standards")
print(f"Loaded version: {voice_domain['version']}")

# 2. Безпечне оновлення домену (з обов'язковою фіксацією в brain_versions)
brain.save_section(
    section="social_media_and_distribution",
    title="Стратегія просування у YouTube та соціальних мережах",
    content=updated_payload,
    version="2.3.0",
    who_id=17,
    change_summary="Додано емпіричний стандарт YouTube Shorts v2.3.0 (хук 3 сек, воронка пов'язаних відео)"
)
```

---

## 3. Реєстр Доменів Пам'яті JERMINA (`v2.3.0`)

1. `core_system_architecture` — Стандарти взаємодії компонентів, 2-годинні цикли ітерацій.
2. `creative_direction_and_style` — Естетика кіберпанку, палітра кольорів, правила шортсів.
3. `voice_and_audio_standards` — Gemini 3.8 Live API WebSocket 24kHz, заборона монотонного TTS, акторські інструкції.
4. `social_media_and_distribution` — YouTube Shorts стратегія (хук 3 сек, приватне завантаження, зв'язок через Related Video).
5. `multi_agent_hierarchy` — Ієрархія субагентів, таблиця `who_id`, заборона AI Brain Main виконувати роботу вручну.
6. `database_and_persistence` — SSOT-структура (`processed_files`, `news`, `digests`, `video_catalog`).
7. `vfx_and_animation_specs` — Специфікація Remotion v4, Three.js, Blender bpy.
8. `news_and_content_strategy` — Пайплайн новин від GDisk до Дайджесту, дедуплікація Gemini 3.5 Flash Lite.
9. `operational_memory_and_incidents` — Архітектурні виправлення та інциденти без сесійного сміття.
10. `studio_governance_and_metrics` — Метрики студії, KPI утримання аудиторії, архів звітів.
