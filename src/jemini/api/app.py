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


@app.get("/health", tags=["General"])
async def health():
    return {"status": "healthy", "engine": "Jemini Core"}

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
    from jemini.core.context import ChannelRegistry
    if not channels:
        for c in ChannelRegistry.list_channels():
            channels[c.channel_id] = c
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


# ----------------- Production Queue Endpoints -----------------
class EnqueueTaskRequest(BaseModel):
    channel_id: str
    topic: str
    metadata: dict[str, Any] | None = None


@app.get("/queue/tasks", tags=["Production Queue"])
async def list_queue_tasks(channel_id: str | None = None):
    """Lists pending, processing, and completed video generation tasks."""
    from jemini.scheduling.queue import ProductionQueue

    queue = ProductionQueue()
    tasks = queue.list_tasks()
    if channel_id:
        tasks = [t for t in tasks if t.channel_id == channel_id]
    return {"total": len(tasks), "tasks": [t.model_dump(mode="json") for t in tasks]}


@app.post("/queue/enqueue", tags=["Production Queue"])
async def enqueue_production_task(req: EnqueueTaskRequest):
    """Enqueues a new topic into the autonomous generation queue."""
    from jemini.scheduling.queue import ProductionQueue

    queue = ProductionQueue()
    task = queue.enqueue(channel_id=req.channel_id, topic=req.topic, metadata=req.metadata)
    return {"status": "enqueued", "task": task.model_dump(mode="json")}


# ----------------- Stickman Kinematics & Motions -----------------
@app.get("/motions", tags=["Stickman Kinematics"])
async def list_motion_presets():
    """Lists registered kinematic acting presets and props from SEMANTIC_ONTOLOGY."""
    from jemini.rendering.semantic_actor import SEMANTIC_ONTOLOGY

    presets = []
    for keywords, anim, eye, mouth, prop, emojis in SEMANTIC_ONTOLOGY:
        presets.append({
            "animation": anim,
            "prop": prop,
            "eye_type": eye,
            "mouth_type": mouth,
            "emojis": emojis,
            "keywords": keywords[:5],
        })
    return {"total_presets": len(presets), "presets": presets}


@app.get("/motions/{preset_name}", tags=["Stickman Kinematics"])
async def get_motion_preset(preset_name: str):
    """Retrieves motion preset configuration by name."""
    from jemini.rendering.semantic_actor import SEMANTIC_ONTOLOGY

    for keywords, anim, eye, mouth, prop, emojis in SEMANTIC_ONTOLOGY:
        if anim.lower() == preset_name.lower():
            return {
                "animation": anim,
                "prop": prop,
                "eye_type": eye,
                "mouth_type": mouth,
                "emojis": emojis,
                "keywords": keywords,
            }
    raise HTTPException(status_code=404, detail=f"Motion preset '{preset_name}' not found.")


# ----------------- YouTube Categories Endpoints -----------------
class CategoryRecommendRequest(BaseModel):
    topic: str
    script_text: str = ""
    tags: list[str] = []


@app.get("/youtube/categories", tags=["YouTube Publishing"])
async def list_youtube_categories():
    """Lists all official YouTube video categories."""
    from jemini.publishing.category_selector import YOUTUBE_CATEGORY_NAMES, YouTubeCategory

    cats = [
        {"id": c.value, "enum_name": c.name, "display_name": YOUTUBE_CATEGORY_NAMES.get(c.value, c.name)}
        for c in YouTubeCategory
    ]
    return {"total_categories": len(cats), "categories": cats}


@app.post("/youtube/categories/recommend", tags=["YouTube Publishing"])
async def recommend_youtube_category(req: CategoryRecommendRequest):
    """Recommends the best YouTube Category ID based on topic, script, and tags."""
    from jemini.publishing.category_selector import CategorySelector

    decision = CategorySelector.select_category(
        title=req.topic,
        description=req.script_text,
        tags=req.tags,
    )
    return decision.model_dump(mode="json")


# ----------------- API Reflection -----------------
@app.get("/api/endpoints", tags=["General"])
async def list_api_endpoints():
    """Returns a full list of registered REST API endpoints in Jemini Core."""
    endpoints = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            endpoints.append({
                "path": route.path,
                "methods": sorted(list(route.methods)),
                "name": route.name,
                "summary": getattr(route, "summary", None) or route.name,
                "tags": getattr(route, "tags", []),
            })
    return {"total_endpoints": len(endpoints), "endpoints": endpoints}

