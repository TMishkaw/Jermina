"""Hierarchical Context Engine & Brain Layers for Jemini.

Layers:
1. Core Base Layer: Universal system rules, commands, invariant guidelines.
2. Domain Knowledge Layer: Domain vertical expertise (scriptwriting, acting, coding).
3. Channel Instance Layer: Channel profile, tone of voice, goals, constraints, baseline metrics.
"""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class ContextLayerType(str, Enum):
    CORE = "core"
    DOMAIN = "domain"
    CHANNEL = "channel"

class ChannelProfile(BaseModel):
    """Channel specific manifest for autonomous operations."""
    channel_id: str
    channel_name: str
    target_platforms: list[str] = Field(default_factory=lambda: ["youtube", "tiktok"])
    core_theme: str
    tone_of_voice: str = "dynamic, captivating, authentic"
    niche_keywords: list[str] = Field(default_factory=list)
    video_language: str = "uk"
    constraints: list[str] = Field(default_factory=list)
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

class ContextLayer(BaseModel):
    layer_type: ContextLayerType
    name: str
    version: str = "1.0.0"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextEngine:
    """Combines and compiles the cascading context layers into an active prompt/instruction."""
    
    def __init__(self, core_layer: Optional[ContextLayer] = None):
        self.core_layer = core_layer or self._default_core_layer()
        self.domain_layers: Dict[str, ContextLayer] = {}
        self.channel_profile: Optional[ChannelProfile] = None

    def _default_core_layer(self) -> ContextLayer:
        return ContextLayer(
            layer_type=ContextLayerType.CORE,
            name="JeminiBaseCore",
            content=(
                "You are an autonomous AI Agent in the Jemini system. "
                "Operate with strict adherence to the Golden Acting Standard, "
                "maintain high agency, generate engaging multimodal content, "
                "and ensure all outputs match the channel identity without deviation."
            )
        )

    def register_domain_layer(self, layer: ContextLayer) -> None:
        self.domain_layers[layer.name] = layer

    def set_channel_profile(self, profile: ChannelProfile) -> None:
        self.channel_profile = profile

    def compile_system_instruction(self, domain_name: Optional[str] = None) -> str:
        """Compile cascading context into unified system instruction."""
        sections = [
            "=== [LAYER 1: CORE ENGINE INVARIANTS] ===",
            self.core_layer.content
        ]
        
        if domain_name and domain_name in self.domain_layers:
            sections.extend([
                f"\n=== [LAYER 2: DOMAIN KNOWLEDGE ({domain_name})] ===",
                self.domain_layers[domain_name].content
            ])
            
        if self.channel_profile:
            profile_summary = (
                f"Channel: {self.channel_profile.channel_name} (ID: {self.channel_profile.channel_id})\n"
                f"Core Theme: {self.channel_profile.core_theme}\n"
                f"Tone of Voice: {self.channel_profile.tone_of_voice}\n"
                f"Platforms: {', '.join(self.channel_profile.target_platforms)}\n"
                f"Constraints: {', '.join(self.channel_profile.constraints) if self.channel_profile.constraints else 'None'}"
            )
            sections.extend([
                "\n=== [LAYER 3: CHANNEL INSTANCE CONTEXT] ===",
                profile_summary
            ])
            
        return "\n\n".join(sections)
