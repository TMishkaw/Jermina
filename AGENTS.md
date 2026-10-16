# Gemini API & Jemini Project Guidelines for AI Agents

## 1. SDK and API Standard
- Always use the modern Gemini API SDK: `google-genai` for Python (`from google import genai`) and `@google/genai` for TypeScript/JavaScript.
- **NEVER** use legacy or deprecated SDKs: `google-generativeai` or `@google/generative-ai`.
- Consult the `geminiDocs` MCP server (`gemini_search_docs` / `gemini_get_doc`) or `https://ai.google.dev/gemini-api/docs/llms.txt` before writing Gemini API integration code.
- Prefer the Interactions API (`client.interactions.create`) for autonomous multi-turn tasks.

## 2. Model Selection & Quota Discipline
- Use modern models exclusively:
  - **Live API & Audio Synthesis**: `gemini-3.8-live` (Unlimited RPM/RPD, 65K TPM).
  - **High-Volume / Routine Tasks**: `gemini-3.1-flash-lite` or `gemini-3.5-flash-lite` (500 RPD, 15 RPM).
  - **Complex Reasoning & Planning**: `gemini-3.8-flash` or `gemini-2.5-pro`.
  - **Vector Memory Embeddings**: `gemini-embedding-2` (1K RPD, 100 RPM).
- Never use deprecated `gemini-1.5-*` models.

## 3. Golden Acting Standard for Voice Synthesis
- Voice synthesis MUST be executed through Gemini 3.8 Live API WebSocket (24kHz PCM mono).
- Never write or pronounce robotic "ha-ha" — use organic chuckles through words and exclamations (`«Пфф!..»`, `«Ой, не можу...»`).
- Adhere to the voice catalog: `Zephyr` (drive/humor/drama), `Aoede` (vocal fry/whisper/seduction), `Fenrir` (brutal bass/cyborg), `Kore` (timid android/fragility).

## 4. Architecture & Git Flow
- All library improvements go strictly into the `dev` branch.
- Zero-leak policy: never commit secret API keys or credentials.

## 5. Determinism vs. Flexibility Matrix
- **Core & Engine (Strictly Deterministic):** Git Flow, Key Rotator + 429 Hot Standby, PostgreSQL schemas, strict typing & ruff/pytest.
- **AI & Context Layers (Hybrid):** Layered hierarchy is invariant (Core -> Domain -> Channel); channel prompts and pgvector memory are flexible.
- **Multimodal Streams (Adaptive with Rigid Triggers):** Deterministic scenarios A/B/C and graceful degradation; flexible real-time visual interpretation.
- **Self-Evolution (Bounded Exploration):** Anchor niche is immutable; creative hypotheses and GitHub Issues generation are autonomous.

## 6. Root-Cause First (Development RCA Protocol)
- **Zero Quick-Fix Policy:** Never use blind `try-except pass` or local workarounds that mask symptoms.
- **Step 1 (RCA):** Uncover why the schema, type, or contract permitted the failure.
- **Step 2 (Systemic Fix):** Fix the architectural contract (Pydantic v2 model, interface, base class).
- **Step 3 (Defect Fix):** Resolve the localized bug.
- **Step 4 (Regression Lock):** Write a dedicated isolated `pytest` unit test reproducing the exact failure before merging to `dev`.

