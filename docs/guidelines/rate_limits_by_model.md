# Peak Usage & Rate Limits by Model (Jemini Workstation Tier)

## 1. Operational Quotas & Limits per Key (Google AI Studio Free Tier)

| Model Name | Architectural Role in Jemini | RPM (Req/Min) | TPM (Tokens/Min) | RPD (Req/Day) | Cooldown on 429 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`gemini-3.8-live`** | Real-time WebSocket Voice & Video Review | **Unlimited** | **65,000** | **Unlimited** | Immediate Reconnect (0s) |
| **`gemini-3.8-live-extended-thinking`** | WebSocket with live background reasoning | **Unlimited** | **65,000** | **Unlimited** | Immediate Reconnect (0s) |
| **`gemini-3.8-flash`** | Complex Reasoning, Isolated Vision Audits | 5 | 250,000 | 20 | 60s per key |
| **`gemini-3.1-pro-preview`** | Deep planning, code architecture | 5 | 250,000 | 20 | 60s per key |
| **`gemini-3.1-flash-lite`** | Routine parsing, sentiment, category routing | **15** | 250,000 | **500** | 30s per key |
| **`gemini-3.5-flash-lite`** | High-throughput comments & script scoring | **15** | 250,000 | **500** | 30s per key |
| **`gemini-embedding-2`** | pgvector semantic indexing (768-dim) | **100** | 30,000 | **1,000** | 10s per key |
| **`gemini-2.5-flash-tts`** | Fallback speech synthesis | 3 | 10,000 | 10 | 60s per key |
| **`gemini-3.8-flash-tts`** | High-fidelity voice generation | 3 | 10,000 | 10 | 60s per key |

---

## 2. API Key Rotator & Quota Strategy (`APIKeyRotator`)

### 2.1 Free-Tier First & Hot Standby
- The studio pool maintains **5 active API keys** registered in `settings.gemini_api_keys`.
- Cumulative free daily capacity across 5 keys:
  - `gemini-3.1-flash-lite` / `3.5-flash-lite`: **2,500 RPD** (Requests per Day)
  - `gemini-embedding-2`: **5,000 RPD**
  - `gemini-3.8-live`: **Unlimited audio synthesis and video reviews**

### 2.2 Model-Specific Cooldown Isolation
- Receiving HTTP `429` (Too Many Requests) locks only the pair `[key_id + model_name]`.
- If Key #1 exhausts its quota for `gemini-3.8-flash`, it remains completely active and unblocked for `gemini-3.1-flash-lite` or `gemini-embedding-2`.
- Active streams transparently fail over to the next standby key in $< 50\text{ ms}$.

### 2.3 Spike Handling (503 Service Unavailable)
- Google API capacity spikes trigger immediate key rotation or graceful fallback:
  - If `gemini-3.8-flash` is saturated, tasks fall back to `gemini-3.1-pro-preview` or `gemini-3.5-flash-lite` depending on complexity tier.