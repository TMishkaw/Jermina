# Gemini 3.8 Live API Bidirectional WebSocket Streaming

## 1. Protocol Architecture
Gemini 3.8 Live API operates over full-duplex WebSockets for real-time human-like video reviewing, audio interaction, and speech synthesis:
- **Model Endpoint:** `gemini-3.8-live`
- **Modern SDK:** `google-genai` (`from google import genai`)
- **Connection Method:** `client.aio.live.connect(model="gemini-3.8-live", config=config)`

---

## 2. Audio & Video Data Formats

### 2.1 Multimodal Video Review (Client -> Server)
When evaluating rendered animations in real-time via [`LiveVideoReviewer`](file:///d:/JerminaStudio/JerminaDev/src/jemini/validation/live_reviewer.py):
- **Video Stream:** 1 FPS JPEG frames, 540p width, JPEG quality `q:v 6` ($\approx 22\text{ KB}$ per frame).
- **Audio Stream:** Raw 16kHz 16-bit linear mono PCM (`pcm_s16le`).
- **FFmpeg Extraction Pipeline:**
  ```bash
  # Video frames (1 FPS, 540p)
  ffmpeg -y -i input.mp4 -vf "fps=1,scale=540:-1" -q:v 6 temp_dir/frame_%04d.jpg
  # Audio track (16kHz mono PCM)
  ffmpeg -y -i input.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 -f s16le temp_dir/audio.pcm
  ```

### 2.2 Voice Synthesis (Server -> Client)
- **Output Audio:** 24kHz 16-bit mono PCM stream.
- **Voice Catalog:**
  - `Zephyr`: Dynamic, energetic, ironic humor, dramatic pauses.
  - `Aoede`: Intimate vocal fry, soft whisper, seduction, mystery.
  - `Fenrir`: Brutal, commanding bass, cyborg authority.
  - `Kore`: Android fragility, timid curiosity, precision.
