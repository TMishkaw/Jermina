"""FastAPI REST API application for Jemini Core Engine."""

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from jemini.core.config import settings
from jemini.core.context import ChannelProfile
from jemini.multimodal.live_engine import (
    LiveStreamVisionEvent,
    UniversalLiveEngine,
    VideoReviewReport,
)
from jemini.multimodal.voice import ActingPromptBuilder, VoiceArchetype
from jemini.publisher.base import PublicationPayload
from jemini.publisher.tiktok import TikTokPublisher
from jemini.publisher.youtube import YouTubePublisher
from jemini.rotator.rotator import APIKeyRotator
from jemini.storage.models import KeyType
from jemini.wiki.wiki_engine import WikiEngine

app = FastAPI(
    title="Jemini Core API",
    description="Autonomous content generation, publication, multimodal Live API, and evolution engine.",
    version="0.2.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

import json
from pathlib import Path

# Global runtime singletons
rotator = APIKeyRotator()

# Auto-seed from config/api_keys.json or settings
_keys_file = Path("config/api_keys.json")
if _keys_file.exists():
    try:
        with open(_keys_file, "r", encoding="utf-8") as _f:
            _loaded_keys = json.load(_f)
            for _item in _loaded_keys:
                rotator.register_key(
                    key_string=_item.get("key", ""),
                    engine=_item.get("engine", "gemini"),
                    key_type=KeyType(_item.get("key_type", "free")),
                    models_mapping={"name": _item.get("name", "unnamed")}
                )
    except (OSError, json.JSONDecodeError):
        pass
elif settings.gemini_api_keys:
    for _k in settings.gemini_api_keys:
        rotator.register_key(key_string=_k, key_type=KeyType.FREE)

live_engine = UniversalLiveEngine(rotator)
wiki = WikiEngine()
channels: dict[str, ChannelProfile] = {}

class KeyRegisterRequest(BaseModel):
    api_key: str
    engine: str = "gemini"
    key_type: KeyType = KeyType.FREE
    models_mapping: dict[str, Any] | None = None

class VideoEvaluationRequest(BaseModel):
    video_id: str
    video_path: str
    guidelines: str | None = None

class LiveParseRequest(BaseModel):
    session_id: str
    platform: str
    frame_base64: str

class VoiceSynthesisRequest(BaseModel):
    script_text: str
    voice: VoiceArchetype = VoiceArchetype.ZEPHYR
    emotion: str = "viral blogger drive"
    vocal_fry: bool = False

@app.get("/", tags=["General"])
async def root():
    return {
        "engine": "Jemini Core",
        "version": "0.2.0",
        "status": "operational",
        "docs": "/docs",
        "wiki": "/wiki"
    }

# ----------------- Key Rotator Endpoints -----------------
@app.get("/rotator/status", tags=["API Key Rotator"])
async def get_rotator_status():
    """Retrieve per-model health and availability status of API keys."""
    return {"keys": rotator.get_stats()}

@app.post("/rotator/keys", tags=["API Key Rotator"])
async def register_api_key(req: KeyRegisterRequest):
    """Register a new API key with tier (free/paid) and model quotas."""
    rotator.register_key(
        key_string=req.api_key,
        engine=req.engine,
        key_type=req.key_type,
        models_mapping=req.models_mapping,
    )
    return {"message": f"Key registered with type '{req.key_type.value}' in engine '{req.engine}'."}

# ----------------- Live API Multi-modal Endpoints -----------------
@app.post("/live/evaluate", response_model=VideoReviewReport, tags=["Live Multimodal Engine"])
async def evaluate_video(req: VideoEvaluationRequest):
    """Scenario A: Video Intelligence & Evaluation (structured analytical review)."""
    return await live_engine.evaluate_video_content(
        video_id=req.video_id,
        video_bytes_or_path=req.video_path,
        custom_guidelines=req.guidelines,
    )

@app.post("/live/vision-parse", response_model=list[LiveStreamVisionEvent], tags=["Live Multimodal Engine"])
async def parse_stream_frame(req: LiveParseRequest):
    """Scenario B: Live Stream Vision & Parsing (detect gifts, likes, actions on TikTok/YouTube)."""
    return await live_engine.parse_live_stream_frame(
        session_id=req.session_id,
        platform=req.platform,
        frame_bytes=req.frame_base64.encode("utf-8"),
    )

@app.post("/live/voice-tts", tags=["Live Multimodal Engine"])
async def synthesize_voice_tts(req: VoiceSynthesisRequest):
    """Scenario C: AI Voice TTS with actor embodiment following Golden Acting Standard."""
    directive = ActingPromptBuilder.build_acting_directive(
        script_text=req.script_text,
        voice=req.voice,
        emotion=req.emotion,
        include_vocal_fry=req.vocal_fry,
    )
    return {
        "voice": req.voice.value,
        "sample_rate_hz": 24000,
        "directive_prompt": directive,
        "status": "ready_for_pcm_streaming"
    }

# ----------------- Channels & Publishing -----------------
@app.post("/channels/onboard", tags=["Channel Management"])
async def onboard_channel(profile: ChannelProfile):
    channels[profile.channel_id] = profile
    return {
        "status": "success",
        "message": f"Channel '{profile.channel_name}' onboarded successfully.",
        "channel_id": profile.channel_id
    }

@app.get("/channels", tags=["Channel Management"])
async def list_channels():
    return {"channels": list(channels.values())}

@app.post("/publisher/publish/{platform}", tags=["Publisher"])
async def publish_content(platform: str, payload: PublicationPayload):
    if platform.lower() == "youtube":
        publisher = YouTubePublisher()
    elif platform.lower() == "tiktok":
        publisher = TikTokPublisher()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform '{platform}'.")

    return await publisher.publish(payload)

@app.get("/wiki", response_class=HTMLResponse, tags=["Wiki"])
async def get_wiki_html():
    return wiki.render_html()
