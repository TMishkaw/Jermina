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
- All library improvements go strictly into the `dev` branch via Pull Requests adhering to [`.github/PULL_REQUEST_TEMPLATE.md`](file:///d:/JerminaStudio/JerminaDev/.github/PULL_REQUEST_TEMPLATE.md).
- Adhere strictly to the guidelines, Conventional Commits, and branch naming conventions in [`CONTRIBUTING.md`](file:///d:/JerminaStudio/JerminaDev/CONTRIBUTING.md).
- Zero-leak policy: never commit secret API keys, tokens, or credentials (`config/client_secret.json` is git-ignored).

## 5. Determinism vs. Flexibility Matrix
- **Core & Engine (Strictly Deterministic):** Git Flow, Key Rotator + 429 Hot Standby, PostgreSQL schemas, strict typing & ruff/pytest.
- **AI & Context Layers (Hybrid):** Layered hierarchy is invariant (Core -> Domain -> Channel); channel prompts and pgvector memory are flexible.
- **Multimodal Streams (Adaptive with Rigid Triggers):** Deterministic scenarios A/B/C and graceful degradation; flexible real-time visual interpretation.
- **Self-Evolution (Bounded Exploration):** Anchor niche is immutable; creative hypotheses and GitHub Issues generation are autonomous, adhering to [`.github/ISSUE_TEMPLATE/03_agent_hypothesis.yml`](file:///d:/JerminaStudio/JerminaDev/.github/ISSUE_TEMPLATE/03_agent_hypothesis.yml) with structured labels (`type:agent-hypothesis`, `origin:agent-*`).

## 6. Root-Cause First (Development RCA Protocol)
- **Zero Quick-Fix Policy:** Never use blind `try-except pass` or local workarounds that mask symptoms.
- **Step 1 (RCA):** Uncover why the schema, type, or contract permitted the failure (documented via [`.github/ISSUE_TEMPLATE/01_defect_rca.yml`](file:///d:/JerminaStudio/JerminaDev/.github/ISSUE_TEMPLATE/01_defect_rca.yml)).
- **Step 2 (Systemic Fix):** Fix the architectural contract (Pydantic v2 model, interface, base class).
- **Step 3 (Defect Fix):** Resolve the localized bug.
- **Step 4 (Regression Lock):** Write a dedicated isolated `pytest` unit test reproducing the exact failure before merging to `dev`.

## 7. Visual Acting & Pacing Standard (Stickman Kinematics)
- **Pacing Constraint (5–10 Presets):** Videos must feature exactly 5 to 10 deliberate acting beats (`target_count_range=(5, 10)`), with natural staging duration (~3.5–5.5 seconds per pose). Micro-cue flickering (<1.5s) and spastic prop cycling are strictly prohibited.
- **S-Curve Pose Blending:** 12-frame smoothstep interpolation (`interpolatePose`) between all consecutive cue transitions to eliminate robotic angle snapping.
- **Overlapping Action:** Forearms must lag shoulders by $\approx 90\text{ ms}$ (secondary motion) to break mechanical metronome movement.
- **Organic Bezier Spine:** The spine is rendered via a curved quadratic Bezier path (`M 0 hip Q spineBend mid 0 shoulder`) with continuous breathing flex.
- **Audio RMS Reactivity:** Live speech volume (`audioRms`) drives gesture amplitude and nodding cadence.
- **Autonomous A/B Testing Evolution:** Missing gestures or uncovered topics trigger `MovementABTester` evaluated by `gemini-3.8-live`. A winning preset is committed to PostgreSQL and `MotionLibraryManager` ONLY after **2 consecutive wins**.

## 8. Database Persistence & Zero-Leak Protocol
- **Container Restart Immunity:** All operational knowledge (`agent_memories`, `stickman_motions`, `youtube_*`) must be safely restorable via `jemini db-export` and `jemini db-restore`.
- **Zero-Leak Sanitization:** Never commit API keys or auth tokens to git (`config/client_secret.json` is git-ignored, and `export_sanitized_db` strictly blacklists secret tables).
- **Automated Pre-Commit Hook:** `.git/hooks/pre-commit` runs on every git commit, automatically dumping fresh sanitized JSON tables into `seeds/sanitized_db/`.

## 9. Gemini 3.8 Live API Constraints
- **WebSocket Parameters:** Do NOT pass `thinking_config` inside `LiveConnectConfig` when opening real-time audio/video review WebSockets (causes close code `1007`). Extended thinking config is only supported on standard `client.models.generate_content`.
- **Streaming Audio/Video:** Stream 1 FPS video frames and 16kHz mono PCM chunks for multimodal evaluation.


