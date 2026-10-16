# Jemini Core & Studio API Reference Specification

## 1. Overview
This specification details all interfaces, REST API endpoints, Pydantic contracts, and programmatic SDK modules of the Jemini platform. All endpoints are accessible via FastAPI (`http://localhost:8000`), in-process testing via `jemini_api_call`, and through the `jemini-studio-docs` Model Context Protocol (MCP) server.

---

## 2. REST API Endpoints Specification

### 2.1 General & Health
- **`GET /`**
  - **Summary:** Root service metadata and discovery links.
  - **Response (200):** `{"engine": "Jemini Core", "version": "0.2.0", "status": "operational", "docs": "/docs", "wiki": "/wiki"}`
- **`GET /health`**
  - **Summary:** Operational readiness probe.
  - **Response (200):** `{"status": "healthy", "engine": "Jemini Core"}`
- **`GET /api/endpoints`**
  - **Summary:** Reflection endpoint listing all registered routes, HTTP methods, and tags.
- **`GET /docs` & `GET /redoc`**
  - **Summary:** Swagger UI and ReDoc OpenAPI documentation.
- **`GET /wiki`**
  - **Summary:** Rendered HTML view of Jemini Autonomous Knowledge Base.

---

### 2.2 API Key Rotator & Quota Accounting
- **`GET /rotator/status`**
  - **Summary:** Per-key and per-model availability statistics, cooldowns, and failure counters.
  - **Response (200):** `{"keys": [{"key_id": "...", "engine": "gemini", "type": "free", "status": "active", "cooldowns": {...}}]}`
- **`POST /rotator/keys`**
  - **Summary:** Registers a new API key with tier (`free` or `paid`) and custom model mapping.
  - **Request Body:**
    ```json
    {
      "api_key": "AIzaSy...",
      "engine": "gemini",
      "key_type": "free",
      "models_mapping": {"name": "primary_key"}
    }
    ```
  - **Response (200):** `{"message": "Key registered with type 'free' in engine 'gemini'."}`

---

### 2.3 Gemini Live Multimodal Engine
- **`POST /live/evaluate`**
  - **Summary:** Scenario A: Video Intelligence & Evaluation. Analyzes video frames and audio against 3-second hook criteria and Golden Acting Standard.
  - **Request Body:**
    ```json
    {
      "video_id": "short_001",
      "video_path": "output/videos/test.mp4",
      "guidelines": "Check 3-second hook and audio RMS intensity"
    }
    ```
  - **Response (200):** `VideoReviewReport` (JSON report with hook_score, pacing_score, vocal_score, recommendations).
- **`POST /live/vision-parse`**
  - **Summary:** Scenario B: Live Stream Vision & Parsing. Extracts real-time viewer events, gifts, comments, and screen actions.
  - **Request Body:**
    ```json
    {
      "session_id": "live_stream_yt_12",
      "platform": "youtube",
      "frame_base64": "<base64_jpeg_data>"
    }
    ```
  - **Response (200):** `list[LiveStreamVisionEvent]`
- **`POST /live/voice-tts`**
  - **Summary:** Scenario C: Voice synthesis acting directive generation for Gemini 3.8 Live API WebSocket.
  - **Request Body:**
    ```json
    {
      "script_text": "Стоп! Що це за парадокс?",
      "voice": "Zephyr",
      "emotion": "viral blogger drive",
      "vocal_fry": false
    }
    ```
  - **Response (200):** `{"voice": "Zephyr", "sample_rate_hz": 24000, "directive_prompt": "...", "status": "ready_for_pcm_streaming"}`

---

### 2.4 Channel Management & Publishing
- **`GET /channels`**
  - **Summary:** Lists all configured channel profiles in `ChannelRegistry`.
  - **Response (200):** `{"channels": [ChannelProfile, ...]}`
- **`POST /channels/onboard`**
  - **Summary:** Onboards or registers a new channel profile.
  - **Request Body:** `ChannelProfile` (channel_id, channel_name, core_theme, accent_color, voice_name, default_tags).
- **`POST /publisher/publish/{platform}`**
  - **Summary:** Publishes finalized video asset to YouTube Shorts or TikTok.
  - **Path Parameter:** `platform` (`youtube` | `tiktok`).
  - **Request Body:** `PublicationPayload` (video_path, title, description, tags, category_id, scheduled_time, is_public).

---

### 2.5 Production Queue
- **`GET /queue/tasks`**
  - **Summary:** Lists queued, processing, and completed generation tasks.
  - **Query Parameters:** `channel_id` (optional).
  - **Response (200):** `{"total": 3, "tasks": [ProductionTask, ...]}`
- **`POST /queue/enqueue`**
  - **Summary:** Adds a topic into the autonomous generation queue.
  - **Request Body:**
    ```json
    {
      "channel_id": "tech_channel",
      "topic": "Gemini 3.8 Live API Architecture",
      "metadata": {"priority": 1}
    }
    ```
  - **Response (200):** `{"status": "enqueued", "task": ProductionTask}`

---

### 2.6 Stickman Kinematics & Motions
- **`GET /motions`**
  - **Summary:** Lists all registered kinematic acting presets, props, and associated emojis from `SEMANTIC_ONTOLOGY`.
  - **Response (200):** `{"total_presets": 14, "presets": [{"animation": "stop", "prop": "stop_sign", ...}]}`
- **`GET /motions/{preset_name}`**
  - **Summary:** Retrieves details and kinematic triggers for a specific preset (e.g. `stop`, `point`, `think`, `shrug`).
  - **Response (200):** `{"animation": "stop", "prop": "stop_sign", "eye_type": "wide", "mouth_type": "gasp", "emojis": ["🛑", "✋"], "keywords": [...]}`

---

### 2.7 YouTube Categories & Semantic Classification
- **`GET /youtube/categories`**
  - **Summary:** Lists all 31 official YouTube Video Categories with numeric ID and display name.
  - **Response (200):** `{"total_categories": 31, "categories": [{"id": "28", "enum_name": "SCIENCE_AND_TECHNOLOGY", "display_name": "Science & Technology"}, ...]}`
- **`POST /youtube/categories/recommend`**
  - **Summary:** Analyzes title, script, and hashtags to classify video into optimal algorithmic YouTube Category.
  - **Request Body:**
    ```json
    {
      "topic": "Як штучний інтелект Gemini 3.8 кодить",
      "script_text": "Розбір нових мультимодальних моделей",
      "tags": ["#AI", "#Python", "#Gemini"]
    }
    ```
  - **Response (200):** `CategoryMatchResult` (category_id="28", category_name="Science & Technology", confidence_score=4.0).

---

## 3. Python SDK Programmatic Interfaces

| Class / Module | Import Path | Architectural Role |
| :--- | :--- | :--- |
| **`APIKeyRotator`** | `jemini.rotator.rotator` | Manages 5-key API pool, hot standby, 429 key+model isolation, and task routing. |
| **`UniversalLiveEngine`** | `jemini.multimodal.live_engine` | Multi-scenario coordinator for Live API WebSocket video review, vision parsing, and voice TTS. |
| **`CategorySelector`** | `jemini.publishing.category_selector` | 31-category semantic YouTube classifier with keyword weighting. |
| **`ProductionQueue`** | `jemini.scheduling.queue` | JSON file-backed production task queue with atomic state transitions. |
| **`SemanticActor`** | `jemini.rendering.semantic_actor` | Spoken Ukrainian lexical semantic parser mapping speech to physical stickman cues. |
| **`IsolatedMotionRenderer`** | `jemini.validation.live_motion_auditor` | Headless Remotion single-frame stickman renderer for visual blind audits. |
| **`MovementABTester`** | `jemini.validation.ab_testing` | Double-blind 2-win convergence coordinator using `gemini-3.8-live`. |
| **`StudioDocsEngine`** | `jemini.mcp.studio_docs` | Recursive token-based documentation indexer and search engine across `docs/`. |
| **`MCPServer`** | `jemini.mcp.server` | Zero-dependency JSON-RPC 2.0 stdio Model Context Protocol server. |

---

## 4. MCP Tools Catalog (`jemini-studio-docs`)

Agents running in Antigravity or any MCP client can interact with Jemini via the following 7 tools:

1. **`jemini_search_docs`**: Token search across all documentation in `docs/` (`studio_knowledge`, `wiki`, `guidelines`).
2. **`jemini_get_doc`**: Fetches full Markdown content of a specified document by name or relative path.
3. **`jemini_list_docs`**: Catalogs all markdown files with sections, titles, and byte sizes.
4. **`jemini_list_sections`**: Lists all active documentation sections (`DevDocs`, `LiveAPIDocs`, `PublishingDocs`, `VideoProductionDocs`, `wiki`, `guidelines`).
5. **`jemini_list_api_endpoints`**: Markdown table of all REST API routes, HTTP methods, and operation summaries.
6. **`jemini_api_schema`**: OpenAPI 3.1.0 schema specification for all endpoints or filtered by path.
7. **`jemini_api_call`**: In-process execution of any REST API endpoint via `TestClient(app)` returning HTTP status code and JSON payload.
