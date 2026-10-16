# Gemini Live API Critical Constraints & Gotchas

## 1. The 1007 Close Code Bug (thinking_config inside LiveConnectConfig)
> [!CAUTION]
> **DO NOT** pass `thinking_config` inside `LiveConnectConfig` when establishing a real-time WebSocket connection to `gemini-3.8-live`. Doing so triggers an immediate abnormal WebSocket termination with close code `1007` (Invalid Frame Payload Data).
> 
> Extended reasoning (`thinking_config`) is strictly supported on standard request-response calls via `client.models.generate_content`, **never** on streaming WebSockets.

### Correct LiveConnectConfig:
```python
from google.genai import types

# CORRECT: Clean LiveConnectConfig for gemini-3.8-live
config = types.LiveConnectConfig(
    response_modalities=[types.LiveModality.AUDIO],
    speech_config=types.SpeechConfig(
        voice_config=types.VoiceConfig(
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
        )
    ),
    system_instruction=types.Content(
        parts=[types.Part.from_text(text="Ти — Режисер анімації...")]
    ),
)
```

---

## 2. Model Deprecation & Selection Rules
- **NEVER use:** `gemini-1.5-*`, `gemini-2.0-*`, or `gemini-2.5-pro` (deprecated/retired by Google).
- **Mandatory Modern Models:**
  - Real-Time Live Streaming: `gemini-3.8-live` (unlimited RPM/RPD).
  - Complex Reasoning & Still Image Vision: `gemini-3.8-flash` or `gemini-3.1-pro-preview`.
  - High-Volume / Semantic Routing: `gemini-3.1-flash-lite` or `gemini-3.5-flash-lite`.
  - Embeddings: `gemini-embedding-2`.

---

## 3. Quota Management & Hot-Standby Rotator
- Handle HTTP `429` (Rate Limit) and `503` (High Demand Spikes) via [`APIKeyRotator`](file:///d:/JerminaStudio/JerminaDev/src/jemini/rotator/rotator.py).
- Keys automatically cycle upon encountering non-200 responses.
