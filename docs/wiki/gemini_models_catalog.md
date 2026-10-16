# Повний каталог моделей Gemini API (Official Reference)

> Джерело: Офіційна документація Google Gemini API ([ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models))

---

## 1. Сімейство Gemini 3 (Текстові та Мультимодальні моделі)

| Модель | Ендпоінт (Model ID) | Статус | Призначення та особливості |
| :--- | :--- | :--- | :--- |
| **Gemini 3.8 Flash** | `gemini-3.8-flash` | **New Stable** | Найрозумніша Flash-модель для автономних агентів, складного інжинірингу та тривалих workflow. |
| **Gemini 3.8 Live** | `gemini-3.8-live` | **New Stable** | Дефолтна модель Live API для низьколатентних голосових агентів без затримок на міркування. |
| **Gemini 3.8 Live Extended Thinking** | `gemini-3.8-live-extended-thinking` | **New Stable** | Live API з глибоким фоновим міркуванням під час живих голосових взаємодій. |
| **Gemini 3.8 Flash TTS** | `gemini-3.8-flash-tts` | **New Stable** | Флагманський синтез мовлення для акторської гри, дизайну голосу та реплікації (130 мов). |
| **Gemini 3.8 Flash-Lite TTS** | `gemini-3.8-flash-lite-tts` | **New Stable** | Швидкий, ультра-економічний TTS для високонавантажених сервісів (101 мова). |
| **Gemini 3.6 Flash** | `gemini-3.6-flash` | **Stable** | Збалансована швидкість та мультимодальність для щоденних задач. |
| **Gemini 3.5 Flash-Lite** | `gemini-3.5-flash-lite` | **Stable** | Високошвидкісне виконання рутинних операцій (**500 RPD** на Free Tier). |
| **Gemini 3.1 Flash-Lite** | `gemini-3.1-flash-lite` | **Stable** | Флагманська продуктивність за мінімальну вартість (**500 RPD**, 15 RPM). |
| **Gemini 3.1 Pro** | `gemini-3.1-pro-preview` | **Preview** | Просунутий інтелект, складне розв'язання проблем та vibe coding. |
| **Gemini 3.5 Transcribe** | `gemini-3.5-transcribe` | **New Stable** | Розпізнавання мови з diarization спікерів та таймстемпами слів. |
| **Gemini 3.5 Live Translate** | `gemini-3.5-live-translate-preview` | **Preview** | Синхронний двосторонній переклад мови в реальному часі для 70+ мов. |

---

## 2. Генеративні медіа-моделі (Відео, Зображення, Музика)

### Відео
- **Veo 3.1** (`veo-3.1-generate-preview`): кінематографічна генерація відео зі синхронізованим нативним звуком.
- **Veo 3.1 Lite** (`veo-3.1-lite-generate-preview`): легка, високошвидкісна генерація та монтаж відео.
- **Gemini Omni Flash** (`gemini-omni-1.1-flash`): швидка генерація, інтерполяція ключових кадрів та редагування відео зі звуком.

### Зображення (Nano Banana)
- **Nano Banana 2.1** (`gemini-nano-banana-2.1`): топова генерація зображень з покращеною типографікою та консистентністю персонажів.
- **Nano Banana 2** (`gemini-3.1-flash-image`): висока швидкість для масштабованого контенту.
- **Nano Banana 2 Lite** (`gemini-3.1-flash-lite-image`): наднизька затримка для інтерактивних сервісів.
- **Nano Banana Pro** (`gemini-3-pro-image`): професійні visual assets у 4K з міркуванням над композицією.

### Музика та саундтреки
- **Lyria 3.5** (`lyria-3.5`): флагманська генерація повноцінних пісень зі складною структурою.
- **Lyria 3 Clip** (`lyria-3-clip-preview`): короткі музичні фрагменти та лупи до 30 секунд.
- **Lyria RealTime** (`lyria-realtime-exp`): стрімінгова генерація музики в реальному часі.

---

## 3. Спеціалізовані та векторні моделі (Embeddings & Agents)

- **Gemini Embedding 2** (`gemini-embedding-2-preview`): **перша мультимодальна векторна модель**, що конвертує текст, аудіо, зображення, відео та PDF в єдиний 768-вимірний векторний простір для pgvector RAG-систем.
- **Gemini Deep Research** (`deep-research-preview-04-2026`): автономне планування та дослідження сотень джерел із формуванням звітів.
- **Antigravity Agent** (`antigravity-preview-09-2026`): керований автономний агент в ізольованому Linux sandbox.

---

## 4. Застарілі та вимкнені моделі (Deprecated / Shut Down)

> ⚠️ **Критично**: Категорично заборонено використовувати в коді:
- `gemini-2.0-flash` (Shut down)
- `gemini-2.0-flash-lite` (Shut down)
- `gemini-3-pro-preview` (Shut down)
- `gemini-1.5-*` (Всі версії 1.5 застаріли)
- `imagen-4.0-generate` (Shut down)
