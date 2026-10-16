"""Seed Development Brain Knowledge and Vector Embeddings into PostgreSQL with pgvector.

Embeds all core engineering laws, Gemini API standards, Live API specs,
Golden Acting Standards, and platform features into associative vector memory.
"""

import asyncio
import hashlib
import logging
import math
from typing import Any

from google import genai
from google.genai import types
from sqlalchemy import text

from jemini.core.config import settings
from jemini.storage.database import AsyncSessionLocal, init_db
from jemini.storage.models import AgentMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed_brain")

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIM = 768

def get_deterministic_vector(text_input: str, dim: int = EMBEDDING_DIM) -> list[float]:
    """Generates a normalized deterministic float vector in case API is unreachable."""
    hasher = hashlib.sha256(text_input.encode("utf-8")).digest()
    values = []
    for i in range(dim):
        byte_val = hasher[i % len(hasher)]
        values.append(math.sin(byte_val + i))
    # Normalize to unit length
    norm = math.sqrt(sum(v * v for v in values)) or 1.0
    return [v / norm for v in values]

def compute_embedding(client: genai.Client | None, text_content: str) -> list[float]:
    """Computes a 768-dim embedding via Gemini Embedding 2 or fallback."""
    if client:
        try:
            res = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text_content,
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIM),
            )
            if res.embeddings and len(res.embeddings) > 0:
                values = list(res.embeddings[0].values)
                if len(values) == EMBEDDING_DIM:
                    return values
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Gemini embedding API call failed: {e}. Falling back to deterministic vector.")

    return get_deterministic_vector(text_content, EMBEDDING_DIM)

def load_knowledge_chunks() -> list[dict[str, Any]]:
    """Loads all architectural blueprints, wiki documents, and guidelines."""
    chunks = []

    # 1. SDK Standard & Models Discipline
    chunks.append({
        "title": "Gemini API SDK Standard & Deprecation Bans",
        "category": "context",
        "tags": ["sdk", "google-genai", "interactions-api", "best-practices"],
        "source": "AGENTS.md",
        "content": (
            "Gemini API SDK Standard:\n"
            "- Always use the modern Gemini API SDK: 'google-genai' for Python ('from google import genai') and '@google/genai' for TypeScript/JavaScript.\n"
            "- NEVER use legacy or deprecated SDKs: 'google-generativeai' or '@google/generative-ai'.\n"
            "- Prefer the Interactions API ('client.interactions.create') for autonomous multi-turn tasks.\n"
            "- Consult upstream documentation before writing Gemini integrations."
        )
    })

    # 2. Model Routing & Quotas
    chunks.append({
        "title": "Model Selection, Tier Routing & Quota Discipline",
        "category": "context",
        "tags": ["models", "quotas", "free-tier", "routing", "flash-lite"],
        "source": "docs/guidelines/rate_limits_by_model.md",
        "content": (
            "Model Selection & Quota Discipline:\n"
            "- Live API & Audio Synthesis: 'gemini-3.8-live' (Unlimited RPM/RPD, 65K TPM) or 'gemini-3.8-live-extended-thinking'.\n"
            "- High-Volume Routine Tasks: 'gemini-3.1-flash-lite' or 'gemini-3.5-flash-lite' (500 RPD, 15 RPM). Crucial: 25x higher daily quota than standard Flash!\n"
            "- Complex Reasoning & Planning: 'gemini-3.8-flash' (20 RPD) or 'gemini-2.5-pro' / 'gemini-3.1-pro-preview'.\n"
            "- Vector Memory Embeddings: 'gemini-embedding-2' (1K RPD, 100 RPM, 768 dimensions).\n"
            "- Strict ban on deprecated/shut down models: gemini-1.5-*, gemini-2.0-flash."
        )
    })

    # 3. Golden Acting Standard for Voice Synthesis
    chunks.append({
        "title": "JERMINA Voice Production & Golden Acting Standard",
        "category": "context",
        "tags": ["voice", "live-api", "acting", "audio-synthesis", "timbre"],
        "source": "C:\\Users\\deftechpoint\\.gemini\\config\\plugins\\jermina-voice\\rules\\AGENTS.md",
        "content": (
            "Golden Acting Standard for Voice Synthesis:\n"
            "- Voice synthesis MUST be executed through Gemini 3.8 Live API WebSocket (24kHz PCM mono output, 16kHz input).\n"
            "- Framed as dynamic character acting, not robotic reading.\n"
            "- Ban synthetic 'ha-ha': use organic conversational chuckles, giggles, gasps, and breath catches.\n"
            "- Emotional triggers: phonetic cues '(sigh)', '(chuckle)', stuttering 'w-what... please...', breathless laughing.\n"
            "- Seduction / intimate warmth: vocal fry on low register, audible sighs and whispering.\n"
            "- Voice Catalog:\n"
            "  * Zephyr: blogger drive, laughter (10/10), high drama, domineering.\n"
            "  * Aoede: velvety vocal fry, seductive depth, soothing lullaby, psychotic whisper.\n"
            "  * Fenrir: brutal bass, fury, cyborg/robotics.\n"
            "  * Kore: light trembling timbre, timid android, fragile innocence."
        )
    })

    # 4. Live API Specifications
    chunks.append({
        "title": "Gemini 3.8 Live API Protocol & Streaming Specs",
        "category": "context",
        "tags": ["live-api", "websocket", "streaming", "pcm", "barge-in"],
        "source": "docs/wiki/gemini_live_api_spec.md",
        "content": (
            "Gemini 3.8 Live API Specifications:\n"
            "- Audio input: 16-bit raw PCM, 16 kHz, little-endian, mono.\n"
            "- Audio output: 16-bit raw PCM, 24 kHz, little-endian, mono.\n"
            "- Video/Vision input: JPEG frames streamed at <= 1 FPS.\n"
            "- Protocol: Stateful bidirectional WebSocket with barge-in support, affective dialogue, and asynchronous tool calling.\n"
            "- Modalities: Bidirectional voice, live video understanding, structured tool calling."
        )
    })

    # 5. Key Rotator & Hot Standby
    chunks.append({
        "title": "API Key Rotator, Free-Tier Priority & Hot Standby",
        "category": "context",
        "tags": ["rotator", "hot-standby", "429-handling", "cooldown"],
        "source": "src/jemini/rotator/rotator.py",
        "content": (
            "API Key Rotator & Quota Manager:\n"
            "- Free-Tier Priority: Always consume Free-tier keys first; keep Paid keys in reserve for overflows or heavy workloads.\n"
            "- Model-Specific Cooldown: A 429 error locks strictly the [key + model] pair; light models remain accessible on the same key.\n"
            "- Hot Standby: Seamless failover to an alternate active key immediately upon receiving 429 without dropping active live streams."
        )
    })

    # 6. Universal Live Engine Scenarios
    chunks.append({
        "title": "Universal Live Engine: Scenarios A, B, and C",
        "category": "context",
        "tags": ["live-engine", "video-evaluation", "stream-parsing", "tts"],
        "source": "src/jemini/multimodal/live_engine.py",
        "content": (
            "Universal Live Engine Scenarios:\n"
            "- Scenario A (Video Intelligence): Evaluates video clips, assesses the 3-second hook, visual retention, and adherence to Golden Acting Standard; outputs structured JSON report.\n"
            "- Scenario B (Stream Vision Parsing): Real-time visual parsing of TikTok/YouTube live streams to detect gifts, likes, chat actions, and comments for interactive streamer battles.\n"
            "- Scenario C (AI Voice TTS): Expressive voice synthesis streaming 24kHz PCM audio using character archetypes (Zephyr, Aoede, Fenrir, Kore)."
        )
    })

    # 7. Model Context Protocol (MCP) Integration
    chunks.append({
        "title": "Model Context Protocol (MCP) Architecture",
        "category": "context",
        "tags": ["mcp", "postgres-jemini", "github", "tools"],
        "source": "docs/wiki/mcp.md",
        "content": (
            "Model Context Protocol (MCP) in Jemini:\n"
            "- Acts as a bridge between agents and external databases, tools, and platforms.\n"
            "- postgres-jemini: Direct live inspection of database schemas, agent memory vectors, and audit logs without manual SQL.\n"
            "- github: Autonomous creation of PRs, issue logging for runtime bugs, branch management.\n"
            "- Configured via .agents/mcp_config.json."
        )
    })

    # 8. Antigravity Platform Features & Custom Subagents
    chunks.append({
        "title": "Antigravity Custom Subagents & Automation Architecture",
        "category": "context",
        "tags": ["subagents", "antigravity", "worktrees", "video-evaluator"],
        "source": "docs/wiki/subagents.md",
        "content": (
            "Antigravity Platform Features & Custom Subagents:\n"
            "- Workspace modes: 'branch' creates isolated Git worktrees for parallel background sweeps without disrupting active workspace.\n"
            "- Context isolation: Subagents start with clean context windows.\n"
            "- Pre-packaged subagents: 'research' (codebase sweeps), 'video-evaluator' (retention and acting audit), 'self' (clone of parent agent).\n"
            "- Declarative Markdown format (.md) with YAML frontmatter in .agents/agents/."
        )
    })

    # 9. Global Quality Gates & Engineering Law
    chunks.append({
        "title": "Global Quality Gates, Git Flow & Zero-Leak Security",
        "category": "context",
        "tags": ["git-flow", "security", "zero-leak", "ruff", "pytest"],
        "source": "docs/wiki/git_flow.md",
        "content": (
            "Quality Gates & Engineering Law:\n"
            "- Zero-leak security: Never commit API keys, secrets, or .env files; track only .example templates.\n"
            "- Git Flow: All active development and library features merge into the 'dev' branch.\n"
            "- Testing standard: 100% pass on pytest unit/integration tests and zero ruff lint errors before release.\n"
            "- Graceful degradation: Subsystem failures never crash the core agent loop."
        )
    })

    return chunks

async def seed_memory():
    logger.info("Initializing database tables...")
    await init_db()

    # Initialize Gemini client using first available API key
    client = None
    if settings.gemini_api_keys:
        primary_key = settings.gemini_api_keys[0]
        client = genai.Client(api_key=primary_key)
        logger.info(f"Connected Gemini client with key {primary_key[:6]}...{primary_key[-4:]}")

    chunks = load_knowledge_chunks()
    logger.info(f"Loaded {len(chunks)} architectural knowledge chunks.")

    async with AsyncSessionLocal() as session:
        # Clear existing development brain entries
        await session.execute(
            text("DELETE FROM agent_memories WHERE channel_id = 'development_brain';")
        )
        await session.commit()
        logger.info("Cleared prior development brain records.")

        for chunk in chunks:
            logger.info(f"Embedding: {chunk['title']}...")
            vec = compute_embedding(client, chunk["content"])

            record = AgentMemory(
                channel_id="development_brain",
                category=chunk["category"],
                content=f"## {chunk['title']}\n\n{chunk['content']}",
                embedding=vec,
                metadata_json={
                    "title": chunk["title"],
                    "tags": chunk["tags"],
                    "source": chunk["source"],
                    "vector_dimension": len(vec),
                }
            )
            session.add(record)

        await session.commit()
        logger.info(f"Successfully seeded {len(chunks)} knowledge chunks into PostgreSQL 'agent_memories'!")

        # Semantic verification test
        logger.info("Running semantic associative memory verification tests...")
        test_queries = [
            "How to synthesize expressive acting voice with vocal fry and Zephyr?",
            "Which model should be used for routine high volume tasks under free tier?",
            "What are the audio input and output specifications for Gemini 3.8 Live API?",
        ]

        for query in test_queries:
            q_vec = compute_embedding(client, query)
            stmt = text("""
                SELECT id, metadata_json->>'title' as title, (embedding <=> :q_vec) as distance
                FROM agent_memories
                WHERE channel_id = 'development_brain'
                ORDER BY distance ASC
                LIMIT 1;
            """)
            result = await session.execute(stmt, {"q_vec": str(q_vec)})
            row = result.fetchone()
            if row:
                logger.info(f"Query: '{query}' -> Top Match: [{row.title}] (cosine distance: {row.distance:.4f})")

if __name__ == "__main__":
    asyncio.run(seed_memory())
