"""Hierarchical Context Engine & Brain Layers for Jemini.

Layers:
1. Core Base Layer: Universal system rules, commands, invariant guidelines.
2. Domain Knowledge Layer: Domain vertical expertise (development brain, scriptwriting, acting, coding).
3. Channel Instance Layer: Channel profile, tone of voice, goals, constraints, baseline metrics.
"""

from enum import Enum
from typing import Any, ClassVar

from pydantic import BaseModel, Field


class ContextLayerType(str, Enum):
    CORE = "core"
    DOMAIN = "domain"
    CHANNEL = "channel"

class ChannelProfile(BaseModel):
    """Channel specific manifest for autonomous operations."""
    channel_id: str
    channel_name: str
    character_name: str = "Джерміна"
    gender: str = "female"  # "female" or "male"
    target_platforms: list[str] = Field(default_factory=lambda: ["youtube", "tiktok"])
    core_theme: str
    tone_of_voice: str = "dynamic, captivating, authentic"
    niche_keywords: list[str] = Field(default_factory=list)
    video_language: str = "uk"
    accent_color: str = "#00F0FF"
    voice_name: str = "Aoede"  # Default female voice
    default_tags: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    custom_settings: dict[str, Any] = Field(default_factory=dict)

    @property
    def tags(self) -> list[str]:
        """Convenience accessor for default_tags."""
        return self.default_tags


class ChannelRegistry:
    """Registry of pre-configured and dynamic multi-channel profiles."""

    _PROFILES: ClassVar[dict[str, ChannelProfile]] = {
        "stickman_lab": ChannelProfile(
            channel_id="stickman_lab",
            channel_name="Jemini Stickman Lab",
            character_name="Джерміна",
            gender="female",
            core_theme="AI coding, viral tech, and autonomous agents",
            tone_of_voice="energetic, humorous, provocative",
            accent_color="#00F0FF",
            voice_name="Aoede",
            niche_keywords=["AI", "Python", "Autonomous Agents", "Remotion", "Gemini 3.8"],
            default_tags=["#AI", "#Coding", "#Jemini", "#TechShorts", "#Python", "#Shorts"],
        ),
        "cyber_matrix": ChannelProfile(
            channel_id="cyber_matrix",
            channel_name="Cyber Matrix Operations",
            character_name="Кібер-Оператор",
            gender="male",
            core_theme="Cybersecurity, terminal hacking, zero-day vulnerabilities, devops",
            tone_of_voice="tactical, sinister, authoritative",
            accent_color="#00FF66",
            voice_name="Fenrir",
            niche_keywords=["Cybersecurity", "ZeroDay", "Linux", "DevOps", "Ethical Hacking"],
            default_tags=["#CyberSecurity", "#Hacking", "#DevOps", "#Terminal", "#Linux", "#Shorts"],
        ),
        "crypto_pulse": ChannelProfile(
            channel_id="crypto_pulse",
            channel_name="Crypto Pulse & Algo",
            character_name="Крипто-Аналітик",
            gender="female",
            core_theme="Cryptocurrency, algorithmic trading, decentralized protocols",
            tone_of_voice="fast-paced, analytical, urgent",
            accent_color="#FFB800",
            voice_name="Aoede",
            niche_keywords=["Bitcoin", "Ethereum", "AlgoTrading", "Web3", "Smart Contracts"],
            default_tags=["#Crypto", "#FinTech", "#AlgoTrading", "#Bitcoin", "#Trading", "#Shorts"],
        ),
        "science_genesis": ChannelProfile(
            channel_id="science_genesis",
            channel_name="Science Genesis",
            character_name="Стелла",
            gender="female",
            core_theme="Quantum computing, synthetic biology, space exploration",
            tone_of_voice="inspiring, wonder-filled, visionary",
            accent_color="#9D00FF",
            voice_name="Kore",
            niche_keywords=["Quantum Computing", "SpaceX", "BioTech", "Physics", "Future"],
            default_tags=["#Science", "#FutureTech", "#Quantum", "#Space", "#Innovation", "#Shorts"],
        ),
    }

    @classmethod
    def get(cls, channel_id: str) -> ChannelProfile:
        """Retrieves channel profile or falls back to stickman_lab with warning."""
        if channel_id in cls._PROFILES:
            return cls._PROFILES[channel_id]
        return cls._PROFILES["stickman_lab"]

    @classmethod
    def list_channels(cls) -> list[ChannelProfile]:
        """Returns all registered channel profiles."""
        return list(cls._PROFILES.values())

    @classmethod
    def register(cls, profile: ChannelProfile) -> None:
        """Registers or overrides a channel profile."""
        cls._PROFILES[profile.channel_id] = profile


class ContextLayer(BaseModel):
    layer_type: ContextLayerType
    name: str
    version: str = "1.0.0"
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)

class DevelopmentBrain:
    """Pre-compiled Domain Knowledge Layer embedding all engineering standards of Jemini."""

    @classmethod
    def get_layer(cls) -> ContextLayer:
        content = (
            "### [DEVELOPMENT BRAIN & ENGINEERING LAW]\n"
            "1. SDK & API DISCIPLINE:\n"
            "   - Always use official modern SDK: 'google-genai' for Python ('from google import genai') and '@google/genai' for TS/JS.\n"
            "   - NEVER use deprecated SDKs: 'google-generativeai' or '@google/generative-ai'.\n"
            "   - Prefer Interactions API ('client.interactions.create') for multi-turn autonomous agents.\n\n"
            "2. MODEL ROUTING & FREE-TIER DISCIPLINE:\n"
            "   - High-Volume / Routine: 'gemini-3.1-flash-lite' or 'gemini-3.5-flash-lite' (500 RPD, 15 RPM).\n"
            "   - Live API & Speech Synthesis: 'gemini-3.8-live' (Unlimited RPM/RPD, 65K TPM).\n"
            "   - Complex Reasoning & Planning: 'gemini-3.8-flash' or 'gemini-3.1-pro-preview'.\n"
            "   - Vector Memory Embeddings: 'gemini-embedding-2-preview' (1K RPD, 100 RPM) into pgvector.\n"
            "   - NEVER use shut-down or deprecated models: gemini-2.0-flash, gemini-3-pro-preview, gemini-1.5-*.\n\n"
            "3. GEMINI LIVE API TECHNICAL SPECIFICATIONS:\n"
            "   - Audio input: 16-bit raw PCM, 16 kHz, little-endian, mono.\n"
            "   - Audio output: 16-bit raw PCM, 24 kHz, little-endian, mono.\n"
            "   - Vision input: JPEG frames at <= 1 FPS.\n"
            "   - Protocol: Stateful WSS WebSocket with Barge-In, Affective Dialog, and Asynchronous Tool Calling.\n\n"
            "4. KEY ROTATOR & HOT STANDBY:\n"
            "   - Free-tier priority: always consume free keys first, keep paid keys in reserve.\n"
            "   - Model-specific cooldown: 429 locks strictly the [key + model] pair without blocking light models.\n"
            "   - Seamless Hot Standby failover during live streams without disconnecting sessions.\n\n"
            "5. GOLDEN ACTING STANDARD FOR VOICE:\n"
            "   - Zephyr: blogger drive, laughter, drama.\n"
            "   - Aoede: vocal fry, whisper, seductive/intimate depth.\n"
            "   - Fenrir: brutal bass, cyborg/robotics.\n"
            "   - Kore: timid android, fragile bright timbre.\n"
            "   - Ban synthetic 'ha-ha' — produce organic chuckles, breath catches, and sighs through words.\n\n"
            "6. QUALITY GATES & SYSTEM ARCHITECTURE:\n"
            "   - Strict Typing (Pydantic v2, MyPy), zero hardcoded secrets (.env / git-ignored).\n"
            "   - Git Flow: dev branch for active work, Antigravity for testing (issues only), main/release for stable releases.\n"
            "   - Testing Pyramid: 100% pass on unit tests + fault injection for 429 and network failures.\n"
            "   - Graceful degradation and structured JSON logging in PostgreSQL.\n"
            "   - MCP servers: postgres-jemini (DB inspection) and github (autonomous PR/Issue workflows).\n"
            "   - Custom Subagents: isolated Git worktrees ('branch' mode) in .agents/agents/.\n\n"
            "7. DETERMINISM VS. FLEXIBILITY MATRIX (SOLID FOUNDATION - FLEXIBLE AGENTS):\n"
            "   - Core & Engine (Strictly Deterministic): Git Flow, Key Rotator + 429 Hot Standby, PostgreSQL schemas, strict typing & ruff/pytest.\n"
            "   - AI & Context Layers (Hybrid): Layered hierarchy invariant (Core -> Domain -> Channel); channel prompts and pgvector memory flexible.\n"
            "   - Multimodal Streams (Adaptive with Rigid Triggers): Deterministic scenarios A/B/C and graceful degradation; flexible real-time visual parsing.\n"
            "   - Self-Evolution (Bounded Exploration): Channel anchor niche is immutable; creative hypotheses and GitHub Issues generation autonomous.\n\n"
            "8. ROOT-CAUSE FIRST (DEVELOPMENT RCA PROTOCOL):\n"
            "   - Zero Quick-Fix Policy: Never use blind try-except pass or local workarounds that mask symptoms.\n"
            "   - Step 1 (RCA): Analyze why the architecture, contract, or typing permitted the error.\n"
            "   - Step 2 (Systemic Fix): Fix the architectural contract (Pydantic v2 model, interface, base class).\n"
            "   - Step 3 (Defect Fix): Resolve the localized bug only after closing the systemic gap.\n"
            "   - Step 4 (Regression Lock): Write a dedicated isolated pytest test reproducing the exact failure before merging to dev.\n\n"
            "9. 5-STEP ARCHITECTURE AUDIT & VERIFICATION CHECKLIST:\n"
            "   - Step 1 (Determinism & Typing): Pydantic v2 contracts, zero Any, strict ruff/mypy checks, isolated core.\n"
            "   - Step 2 (Database Audit): Declarative schema parity, asyncio.Lock / concurrency protection, in-memory cooldown caching.\n"
            "   - Step 3 (Specialized Engines): Key rotator hot standby, per-model 429 isolation, seamless Live API session wrappers.\n"
            "   - Step 4 (RCA Compliance): 100% adherence to Root-Cause First without local quick-fix workarounds.\n"
            "   - Step 5 (Docs & Memory Parity): Complete documentation and pgvector associative memory synchronization.\n\n"
            "10. AUTONOMOUS MEDIA VALIDATION & QUALITY CONTROL LOOP:\n"
            "   - Zero-Human-In-The-Loop: Virtual Art Director via Gemini Live/Multimodal evaluating generated media vs intent.\n"
            "   - Intent Injection: Every artifact is checked against expected duration, emotion, constraints, and hook retention.\n"
            "   - Typed Validation Cards: Output strictly parsed into ValidationCard (overall_score, issues, recommendations).\n"
            "   - Autonomous Correction Loop: NEEDS_CORRECTION triggers automatic self-correction prompts up to 3 iterations.\n"
            "   - Root-Cause Resolution: Recurring validation failures demand systemic prompt/contract fixes rather than endless retries.\n\n"
            "11. CONCURRENCY, PARALLELISM & TECHNICAL LIMITS:\n"
            "   - Live API Duration Limits: Audio-only <= 15 min, Audio-Video <= 2 min, connection lifetime ~10 min.\n"
            "   - Safe Scene Chunking: Texts chunked to <= 180 words per scene (~60-70s) to completely avoid connection disconnects.\n"
            "   - Multi-Scene Parallel Voice Synthesis: Concurrent synthesis across keys using asyncio.gather with unified audio concatenation.\n"
            "   - Parallel Assets Hub & SFX: Local procedural SFX generation and graphic asset retrieval execute in parallel with TTS.\n"
            "   - Remotion Multi-Core Rendering: Concurrency 4-8 Chromium worker instances for high-throughput headless video output."
        )
        return ContextLayer(
            layer_type=ContextLayerType.DOMAIN,
            name="development_brain",
            version="2.4.0",
            content=content,
            metadata={"domain": "engineering_and_gemini_architecture"}
        )

class ContextEngine:
    """Combines and compiles cascading context layers into an active instruction."""

    def __init__(self, core_layer: ContextLayer | None = None, auto_load_dev_brain: bool = True):
        self.core_layer = core_layer or self._default_core_layer()
        self.domain_layers: dict[str, ContextLayer] = {}
        self.channel_profile: ChannelProfile | None = None

        if auto_load_dev_brain:
            self.load_development_brain()

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

    def load_development_brain(self) -> None:
        """Loads all engineering standards, model catalogs, and live specs into domain context."""
        dev_layer = DevelopmentBrain.get_layer()
        self.register_domain_layer(dev_layer)

    def register_domain_layer(self, layer: ContextLayer) -> None:
        self.domain_layers[layer.name] = layer

    def set_channel_profile(self, profile: ChannelProfile) -> None:
        self.channel_profile = profile

    def compile_system_instruction(self, domain_name: str | None = "development_brain") -> str:
        """Compile cascading context into unified system instruction."""
        sections = [
            "=== [LAYER 1: CORE ENGINE INVARIANTS] ===",
            self.core_layer.content
        ]

        target_domain = domain_name if domain_name in self.domain_layers else None
        if target_domain:
            sections.extend([
                f"\n=== [LAYER 2: DOMAIN KNOWLEDGE ({target_domain})] ===",
                self.domain_layers[target_domain].content
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
