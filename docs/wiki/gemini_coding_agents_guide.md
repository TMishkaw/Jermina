# Google Gemini API & Coding Agents Architectural Guide

> Офіційні джерела: [https://ai.google.dev/gemini-api/docs/coding-agents](https://ai.google.dev/gemini-api/docs/coding-agents) | [https://ai.google.dev/gemini-api/docs/llms.txt](https://ai.google.dev/gemini-api/docs/llms.txt)

---

## 1. Обов'язкові стандарти SDK та середовища

### 1.1 Єдиний легітимний SDK
- **Python:** виключно сучасний SDK `google-genai` (`from google import genai`).
  > [!CAUTION]
  > Використання застарілого `google-generativeai` суворо заборонено через несумісність із новітніми протоколами Live API та Interactions API.
- **TypeScript / JavaScript:** виключно `@google/genai`. Застарілий `@google/generative-ai` заборонено.

### 1.2 Interactions API
- Для автономних агентних циклів, тривалих сесій програмування та покрокового виконання завдань рекомендовано використовувати Interactions API (`client.interactions.create`).

---

## 2. Актуальна матриця моделей Gemini (2026)

| Задача в системі | Цільова модель | Квоти / Пропускна здатність | Особливості та обмеження |
| :--- | :--- | :--- | :--- |
| **Реальний час / Live API WebSocket** | `gemini-3.8-live` | Unlimited RPM/RPD, 65K TPM | Аудіо/відео стрімінг 24kHz/16kHz. Заборонено передавати `thinking_config` у `LiveConnectConfig`. |
| **Складне міркування, аудит, planning** | `gemini-3.8-flash` або `gemini-3.1-pro-preview` | 5 RPM, 250K TPM, 20 RPD (Free) | Підтримка розширеного бюджету мислення (`thinking_budget=1024..4096`). |
| **Рутинні задачі, класифікація, роутинг** | `gemini-3.1-flash-lite` або `gemini-3.5-flash-lite` | 15 RPM, 250K TPM, 500 RPD | Високопродуктивний легкий аналіз тексту, низька затримка. |
| **Векторні ембеддінги (pgvector)** | `gemini-embedding-2` | 100 RPM, 30K TPM, 1K RPD | 768-вимірні вектори для збереження та пошуку в PostgreSQL. |

> [!WARNING]
> Застарілі моделі (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-pro`) виведені з експлуатації Google та недоступні для нових сесій.

---

## 3. Машиночитна документація Google
- Додавання суфікса `.md.txt` до будь-якої URL-адреси на `ai.google.dev` повертає чистий Markdown для парсингу агентами без HTML-структури сайту.
- Глобальний маніфест документації: `https://ai.google.dev/gemini-api/docs/llms.txt`.

---

## 4. Model Context Protocol (MCP) інтеграція
- Документація Google Gemini доступна агентам через MCP-сервер `gemini-api_gemini-api-docs`:
  - `gemini_search_docs(query="...", language="python")`
  - `gemini_get_doc(chunk_id="...")`
