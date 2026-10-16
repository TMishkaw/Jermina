"""FastAPI REST API application for Jemini Core Engine."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any

from jemini.rotator.rotator import APIKeyRotator
from jemini.core.config import settings
from jemini.core.context import ChannelProfile
from jemini.publisher.base import PublicationPayload, PublicationResult
from jemini.publisher.youtube import YouTubePublisher
from jemini.publisher.tiktok import TikTokPublisher
from jemini.wiki.wiki_engine import WikiEngine

app = FastAPI(
    title="Jemini Core API",
    description="Autonomous content generation, publication, and evolution engine powered by Gemini API.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global runtime state
rotator = APIKeyRotator(keys=settings.gemini_api_keys)
wiki = WikiEngine()
channels: Dict[str, ChannelProfile] = {}

class KeyAddRequest(BaseModel):
    api_key: str

@app.get("/", tags=["General"])
async def root():
    return {
        "engine": "Jemini Core",
        "version": "0.1.0",
        "status": "operational",
        "docs": "/docs",
        "wiki": "/wiki"
    }

@app.get("/rotator/status", tags=["API Key Rotator"])
async def get_rotator_status():
    """Retrieve health and availability status of Gemini API keys."""
    return {"keys": rotator.get_stats()}

@app.post("/rotator/keys", tags=["API Key Rotator"])
async def add_api_key(req: KeyAddRequest):
    """Add a new Gemini API key to the active rotation pool."""
    rotator.add_key(req.api_key)
    return {"message": "Key registered in rotator pool."}

@app.post("/channels/onboard", tags=["Channel Management"])
async def onboard_channel(profile: ChannelProfile):
    """Bootstrap and onboard an existing or new content channel."""
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
    """Publish content to target platform (youtube or tiktok)."""
    if platform.lower() == "youtube":
        publisher = YouTubePublisher()
    elif platform.lower() == "tiktok":
        publisher = TikTokPublisher()
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported platform '{platform}'.")

    res = await publisher.publish(payload)
    return res

@app.get("/wiki", response_class=HTMLResponse, tags=["Wiki"])
async def get_wiki_html():
    """Autonomous built-in Wiki documentation portal."""
    return wiki.render_html()
