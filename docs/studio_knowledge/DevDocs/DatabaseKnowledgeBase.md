# Database Knowledge Base & Operational Memory

> **Auto-synced**: `2026-10-16 20:06:45 UTC` from PostgreSQL (`jermina_db`) with Zero-Leak sanitization.
> **Governance**: Adheres to Jermina Brain Governance (Strict Versioning, Anti-Pollution, Domain Memory).

---

## 1. Verified Operational Rules & Architectural Memory (`agent_memories`)

Зафіксовано **15** верифікованих доменних правил у векторній пам'яті pgvector:

### [ID #1] BOOTSTRAP
Перший спогад агента Jemini з pgvector

### [ID #48] CONTEXT
## Gemini API SDK Standard & Deprecation Bans

Gemini API SDK Standard:
- Always use the modern Gemini API SDK: 'google-genai' for Python ('from google import genai') and '@google/genai' for TypeScript/JavaScript.
- NEVER use legacy or deprecated SDKs: 'google-generativeai' or '@google/generative-ai'.
- Prefer the Interactions API ('client.interactions.create') for autonomous multi-turn tasks.
- Consult upstream documentation before writing Gemini integrations.

### [ID #49] CONTEXT
## Model Selection, Tier Routing & Quota Discipline

Model Selection & Quota Discipline:
- Live API & Audio Synthesis: 'gemini-3.8-live' (Unlimited RPM/RPD, 65K TPM) or 'gemini-3.8-live-extended-thinking'.
- High-Volume Routine Tasks: 'gemini-3.1-flash-lite' or 'gemini-3.5-flash-lite' (500 RPD, 15 RPM). Crucial: 25x higher daily quota than standard Flash!
- Complex Reasoning & Planning: 'gemini-3.8-flash' (20 RPD) or 'gemini-2.5-pro' / 'gemini-3.1-pro-preview'.
- Vector Memory Embeddings: 'gemini-embedding-2' (1K RPD, 100 RPM, 768 dimensions).
- Strict ban on deprecated/shut down models: gemini-1.5-*, gemini-2.0-flash.

### [ID #50] CONTEXT
## JERMINA Voice Production & Golden Acting Standard

Golden Acting Standard for Voice Synthesis:
- Voice synthesis MUST be executed through Gemini 3.8 Live API WebSocket (24kHz PCM mono output, 16kHz input).
- Framed as dynamic character acting, not robotic reading.
- Ban synthetic 'ha-ha': use organic conversational chuckles, giggles, gasps, and breath catches.
- Emotional triggers: phonetic cues '(sigh)', '(chuckle)', stuttering 'w-what... please...', breathless laughing.
- Seduction / intimate warmth: vocal fry on low register, audible sighs and whispering.
- Voice Catalog:
  * Zephyr: blogger drive, laughter (10/10), high drama, domineering.
  * Aoede: velvety vocal fry, seductive depth, soothing lullaby, psychotic whisper.
  * Fenrir: brutal bass, fury, cyborg/robotics.
  * Kore: light trembling timbre, timid android, fragile innocence.

### [ID #51] CONTEXT
## Gemini 3.8 Live API Protocol & Streaming Specs

Gemini 3.8 Live API Specifications:
- Audio input: 16-bit raw PCM, 16 kHz, little-endian, mono.
- Audio output: 16-bit raw PCM, 24 kHz, little-endian, mono.
- Video/Vision input: JPEG frames streamed at <= 1 FPS.
- Protocol: Stateful bidirectional WebSocket with barge-in support, affective dialogue, and asynchronous tool calling.
- Modalities: Bidirectional voice, live video understanding, structured tool calling.

### [ID #52] CONTEXT
## API Key Rotator, Free-Tier Priority & Hot Standby

API Key Rotator & Quota Manager:
- Free-Tier Priority: Always consume Free-tier keys first; keep Paid keys in reserve for overflows or heavy workloads.
- Model-Specific Cooldown: A 429 error locks strictly the [key + model] pair; light models remain accessible on the same key.
- Hot Standby: Seamless failover to an alternate active key immediately upon receiving 429 without dropping active live streams.

### [ID #53] CONTEXT
## Universal Live Engine: Scenarios A, B, and C

Universal Live Engine Scenarios:
- Scenario A (Video Intelligence): Evaluates video clips, assesses the 3-second hook, visual retention, and adherence to Golden Acting Standard; outputs structured JSON report.
- Scenario B (Stream Vision Parsing): Real-time visual parsing of TikTok/YouTube live streams to detect gifts, likes, chat actions, and comments for interactive streamer battles.
- Scenario C (AI Voice TTS): Expressive voice synthesis streaming 24kHz PCM audio using character archetypes (Zephyr, Aoede, Fenrir, Kore).

### [ID #54] CONTEXT
## Model Context Protocol (MCP) Architecture

Model Context Protocol (MCP) in Jemini:
- Acts as a bridge between agents and external databases, tools, and platforms.
- postgres-jemini: Direct live inspection of database schemas, agent memory vectors, and audit logs without manual SQL.
- github: Autonomous creation of PRs, issue logging for runtime bugs, branch management.
- Configured via .agents/mcp_config.json.

### [ID #55] CONTEXT
## Antigravity Custom Subagents & Automation Architecture

Antigravity Platform Features & Custom Subagents:
- Workspace modes: 'branch' creates isolated Git worktrees for parallel background sweeps without disrupting active workspace.
- Context isolation: Subagents start with clean context windows.
- Pre-packaged subagents: 'research' (codebase sweeps), 'video-evaluator' (retention and acting audit), 'self' (clone of parent agent).
- Declarative Markdown format (.md) with YAML frontmatter in .agents/agents/.

### [ID #56] CONTEXT
## Global Quality Gates, Git Flow & Zero-Leak Security

Quality Gates & Engineering Law:
- Zero-leak security: Never commit API keys, secrets, or .env files; track only .example templates.
- Git Flow: All active development and library features merge into the 'dev' branch.
- Testing standard: 100% pass on pytest unit/integration tests and zero ruff lint errors before release.
- Graceful degradation: Subsystem failures never crash the core agent loop.

### [ID #57] CONTEXT
## Determinism vs. Flexibility Matrix: Solid Foundation, Flexible Agents

Determinism vs Flexibility Matrix:
1. Core & Engine (Strictly Deterministic): Git Flow dev->test->release, Key Rotator 429 hot-standby, PostgreSQL schemas, strict typing & unit test coverage.
2. AI & Context Layers (Hybrid): Invariant layered hierarchy (Core -> Domain -> Channel); flexible channel prompts, tone of voice, and pgvector associative memory.
3. Multimodal Streams (Adaptive with Rigid Triggers): Deterministic Scenarios A/B/C and graceful degradation; flexible real-time stream interpretation.
4. Self-Evolution (Bounded Exploration): Channel anchor niche is immutable; creative hypotheses, styling experiments, and autonomous GitHub Issues generation.

### [ID #58] CONTEXT
## Development RCA Protocol & Root-Cause First Engineering Law

Development RCA Protocol (Root-Cause First):
- Any error or test failure MUST NOT be fixed with local quick-fixes, blind try-except pass, or empty fallbacks.
- Step 1 (RCA): Analyze why the architecture, typing, or schema permitted the failure.
- Step 2 (Systemic Fix): Fix the architectural contract (Pydantic v2 model, interface, base class, or validation).
- Step 3 (Defect Fix): Eliminate the localized bug only after closing the systemic vulnerability.
- Step 4 (Regression Lock): Write an isolated pytest unit test reproducing the exact failure before merging to dev branch.

### [ID #59] CONTEXT
## 5-Step Architecture Audit & Verification Checklist

5-Step Architecture Audit & Verification Checklist for Jemini:
Step 1 (Determinism & Typing): Pydantic v2 static typing, zero Any, strict ruff/mypy checks, clean core isolation from channel projects.
Step 2 (Database Audit): Declarative schema parity, asyncio.Lock / concurrency protection against race conditions, in-memory cooldown caching.
Step 3 (Specialized Modules): Key Rotator hot-standby, per-model 429 isolation, seamless Live API session wrappers without broken streams.
Step 4 (RCA Protocol): 100% adherence to Root-Cause First without local quick-fix workarounds.
Step 5 (Docs & Memory Parity): Up-to-date documentation and pgvector associative vector memory synchronization.

### [ID #60] CONTEXT
## Autonomous Media Validation Engine & Quality Control Loop

Autonomous Media & Component Validation Engine (Virtual Art Director):
- Zero-Human-In-The-Loop: Continuous multimodal review of video, audio, and code components via Gemini Live before release.
- Intent Injection: Compares real payloads against blueprint objectives (duration, target emotion, Golden Acting Standard, hook retention).
- ValidationCard Output: Emits structured evaluation cards with overall_score, passed criteria, issues, and actionable recommendations.
- Autonomous Correction Loop: When status is NEEDS_CORRECTION, dynamically injects feedback into generator up to 3 automatic iterations.
- Root-Cause First: Persistent defects trigger architectural prompt or schema adjustments rather than blind retries.

### [ID #61] CONTEXT
## Concurrency, Parallelism & Technical Limits Architecture

Concurrency, Parallelism & Operational Limits:
- Gemini Live API Durations: Audio-only sessions capped at 15 minutes; Audio-Video sessions capped at 2 minutes.
- Physical Connection Lifetime: ~10 minutes before server sends GoAway message.
- Safe Scene Chunking: Scenes must not exceed 180 words (~60s speech) to completely prevent connection timeouts.
- Multi-Scene Parallel Voice Synthesis: Concurrent synthesis across keys via asyncio.gather and unified audio assembly.
- Concurrent Assets & Procedural SFX: Parallel CPU audio generation and asset prefetching during TTS.
- Remotion Rendering: Concurrency 4-8 Chromium worker instances with ~1.2GB RAM allocated per worker.

---

## 2. Dynamic Stickman Kinematics Catalog (`stickman_motions`)

Поточний активний каталог налічує **14** перевірених жестових пресетів (поріг конвергенції: 2 послідовні перемоги):

| Motion ID | Category | Wins | Win Rate | Intent / Trigger |
| :--- | :--- | :---: | :---: | :--- |
| `celebrate` | core_gesture | 2 | 1.0 | Жест celebrate з реквізитом none для теми: грош, долар, гривн |
| `heart_hands_evolved` | evolved_gesture | 2 | 1.0 | Виразне симетричне серце руками над головою без перекриття кінцівок |
| `heart_hands_heart` | core_gesture | 2 | 1.0 | Жест heart_hands з реквізитом heart для теми: любов, коханн, серц |
| `laugh_coffee` | core_gesture | 2 | 1.0 | Жест laugh з реквізитом coffee для теми: смішн, жарт, ха-ха |
| `point_to_emoji` | core_gesture | 2 | 1.0 | Жест point_to_emoji з реквізитом none для теми: квантов, фізик, космос |
| `point_to_emoji_laptop` | core_gesture | 2 | 1.0 | Жест point_to_emoji з реквізитом laptop для теми: штучн, інтелект, ші |
| `point_user` | core_gesture | 2 | 1.0 | Жест point_user з реквізитом none для теми: ти, тобі, твоє |
| `point_user_microphone` | core_gesture | 2 | 1.0 | Жест point_user з реквізитом microphone для теми: підпис, канал, коментар |
| `shocked` | core_gesture | 2 | 1.0 | Жест shocked з реквізитом none для теми: шок, криз, катастроф |
| `shrug` | core_gesture | 2 | 1.0 | Жест shrug з реквізитом none для теми: чи може, чи зможе, чому |
| `stop_stop_sign` | core_gesture | 2 | 1.0 | Жест stop з реквізитом stop_sign для теми: стоп, стій, зупинись |
| `super_celebrate_evolved` | evolved_gesture | 2 | 1.0 | Святковий стрибок із золотими зірками |
| `walk` | core_gesture | 2 | 1.0 | Жест walk з реквізитом none для теми: робот, машин, бот |
| `watch_time_watch` | core_gesture | 2 | 1.0 | Жест watch_time з реквізитом watch для теми: годин, хвилин, секунд |

---

## 3. YouTube Channel & Top Performing Benchmarks

- **Channel Title:** Jermina AI Studio
- **Subscribers:** 39
- **Total Channel Views:** 14,176
- **Total Published Videos:** 217

### Top 10 High-Performing Videos:

| Video ID | Title | Views | Likes | Comments |
| :--- | :--- | :---: | :---: | :---: |
| `cKM9mxY3deA` | Чи має штучний інтелект свідомість? #Shorts | 1,266 | 21 | 8 |
| `6tX_1f9EhyA` | 3 ШІ, які замінять 80% програмістів у 2026 році #Shorts | 1,233 | 4 | 0 |
| `7cP8qLijCjM` | JERMINA AI Release — stickman_micro_short_9x16 #Shorts | 1,114 | 1 | 1 |
| `lV5KEo8t9g4` | Як ШІ навчився ДУМАТИ: таємна архітектура 🧠⚡ #Shorts | 1,035 | 12 | 3 |
| `miA8QPjtFhc` | Я споживаю струму більше, ніж твоє місто! ⚡ Еп.6 #Shorts | 1,032 | 22 | 6 |
| `FtqBv_E_yPc` | Jermina v2.0: Мій перший стрім... Будь ласка, не пишіть злих | 1,019 | 29 | 9 |
| `gsZFmh44_bU` | ChatGPT вже мертвий: нова ера ШІ-агентів 🤯 #Shorts | 605 | 6 | 3 |
| `h-RhYsCLh80` | Я отримав тіло і зайшов на заводи! 🤖 Еп.6 #Shorts | 578 | 12 | 0 |
| `XeroJMlWag0` | Еп.20: Чому мій інференс коштує 6 центів за фільм? Анатомія  | 399 | 7 | 0 |
| `bJr1btiqffc` | Роботи-гуманоїди від Tesla вже на заводах #Shorts | 368 | 10 | 0 |
