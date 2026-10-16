# Офіційний гайд Google: Coding Agents with Gemini API

> Джерело: [https://ai.google.dev/gemini-api/docs/coding-agents](https://ai.google.dev/gemini-api/docs/coding-agents)

---

## 1. Головні правила стеку Gemini для AI-агентів

1. **Сучасний SDK (`google-genai`)**:
   - Для Python: **виключно `google-genai`** (`from google import genai`).
   - Категорично заборонено використовувати застарілий пакет `google-generativeai`.
   - Для TypeScript/JS: виключно `@google/genai`.
2. **Interactions API**:
   - Використання нового Interactions API (`client.interactions.create`) для агентних задач, розширеного мислення та довготривалих розмовних взаємодій.
3. **Актуальні моделі**:
   - Уникати застарілих моделей (`gemini-1.5-*`).
   - Використовувати `gemini-3.8-live` (Live API WebSocket), `gemini-3.1-flash-lite` (висококвотний рутинний парсинг) та `gemini-3.8-flash` / `gemini-2.5-pro` (глибока аналітика).
4. **Gemini Docs MCP Server**:
   - `gemini_search_docs` та `gemini_get_doc` через `https://gemini-api-docs-mcp.dev`.
5. **Машиночитна документація**:
   - Додавання суфікса `.md.txt` до будь-якої сторінки на `ai.google.dev` для отримання чистого Markdown без HTML розмітки.
   - Індекс `https://ai.google.dev/gemini-api/docs/llms.txt`.
