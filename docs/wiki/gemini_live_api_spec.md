# Технічна специфікація Gemini Live API (Knowledge Base)

> Джерело: Офіційна документація Google Gemini Live API ([ai.google.dev/gemini-api/docs/live-api](https://ai.google.dev/gemini-api/docs/live-api))

---

## 1. Загальний огляд

**Gemini Live API** забезпечує ультранизьку затримку (low-latency) та двосторонній потік аудіо, відео та тексту в реальному часі. Модель підтримує природний діалог, здатність перебивання (*barge-in*), емоційну адаптацію (*affective dialog*) та нативне виконання інструментів (*function calling*).

---

## 2. Технічні специфікації потоків

| Категорія | Параметри специфікації |
| :--- | :--- |
| **Вхідне аудіо (Input Audio)** | Raw 16-bit PCM audio, **16 kHz**, little-endian, mono |
| **Вихідне аудіо (Output Audio)** | Raw 16-bit PCM audio, **24 kHz**, little-endian, mono |
| **Вхідні зображення (Vision / Video)** | JPEG фрейми з частотою **<= 1 FPS** |
| **Протокол передачі** | Stateful WebSocket connection (WSS) |
| **Моделі рушія** | `gemini-3.8-live`, `gemini-3.8-live-extended-thinking` |
| **Квоти Free-Tier** | **RPM = Unlimited**, **RPD = Unlimited**, **TPM = 65 000** |

---

## 3. Ключові можливості

1. **Barge-in (Перебивання)**:
   - Користувач або зовнішній потік може перервати відповідь моделі в будь-який момент, і синтез миттєво зупиняється без зависання буфера.
2. **Affective Dialog & Proactive Audio**:
   - Адаптація тону та стилю мовлення під настрій та експресію вхідного повідомлення.
   - Контроль того, коли модель вступає в розмову (proactive audio).
3. **Tool Use & Function Calling**:
   - Асинхронний виклик інструментів під час голосового або відео-діалогу без розриву аудіопотоку.
4. **Live Transcription & Live Translation**:
   - Двостороннє транскрибування та синхронний переклад для 70+ мов.

---

## 4. Архітектурні підходи розгортання

- **Server-to-Server (Бекенд Jemini)**:
  - Серверний рушій Jemini тримає постійне WebSocket-з'єднання з Live API.
  - Аудіо- та відеотреки стрімів обробляються централізовано.
  - Використовується централізований пул API-ключів через `APIKeyRotator`.
- **Client-to-Server (Фронтенд / Мобільні клієнти)**:
  - Пряме з'єднання клієнтського застосунку з Live API.
  - Для безпеки обов'язково застосовуються **тимчасові ефемерні токени (Ephemeral Tokens)** замість передачі секретних API-ключів.

---

## 5. Інтеграція в екосистемі Jemini

У кодовій базі Jemini двигун Live API реалізовано у:
- **`src/jemini/multimodal/live_engine.py`**: універсальний координатор для відеоаналізу, парсингу стрімів TikTok/YouTube та голосового акторського озвучення (Golden Acting Standard).
- **`src/jemini/multimodal/live_stream.py`**: сесійний WebSocket-клієнт із підтримкою Hot Standby.
