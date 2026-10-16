---
name: jemini-studio-docs
description: Fast retrieval of Jermina Studio architecture, kinematics, Gemini Live API streaming, video production, and publishing standards from docs/studio_knowledge.
---

# Jermina Studio Knowledge & Architectural Docs (`JeminiStudioMCPDocs`)

Use this skill whenever you need authoritative specifications, architectural contracts, or rules regarding:
1. **Stickman Kinematics & Rigging:** Angle geometry ($-\theta$ left, $+\theta$ right), S-curve pose blending, quadratic Bezier spine, secondary motion ($\approx 90\text{ms}$ lag), and isolated testing on `IsolatedMotionCanvas`.
2. **Gemini Live API & Audio:** 24kHz PCM mono for voice synthesis, 16kHz PCM mono for reviews, 1 FPS 540p JPEG frames ($\approx 22\text{KB}$), and strict avoidance of `thinking_config` inside `LiveConnectConfig` (code 1007).
3. **Motion Library & Vector Memory:** `MotionLibraryManager`, PostgreSQL `stickman_motions`, `gemini-embedding-2` pgvector retrieval, and 2-consecutive-wins A/B convergence.
4. **Remotion Hardware Acceleration:** 6-core concurrency, Intel QuickSync + NVIDIA MX130 CUDA workload partitioning, bundle caching, and fast x264 rendering.
5. **Golden Acting Standard & Voice Production:** Zephyr / Aoede / Fenrir / Kore voice archetypes, organic laughing without phonetic "ha-ha", 5–10 presets pacing per video.
6. **YouTube Publishing & Category Selection:** Dynamic category mapping (28 Science, 27 Education, 24 Entertainment), watcher crons, and Zero-Leak pre-commit DB exports.

---

## Document Index & Direct File Links

| Section | Topic | File Path |
| :--- | :--- | :--- |
| **DevDocs** | Stickman Kinematic Angles & Rigging | [`StickmanKinematics.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/DevDocs/StickmanKinematics.md) |
| **DevDocs** | Motion Library & pgvector Storage | [`MotionLibraryPgvector.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/DevDocs/MotionLibraryPgvector.md) |
| **DevDocs** | Remotion Hardware & Isolated Canvas | [`RemotionHardwareGPU.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/DevDocs/RemotionHardwareGPU.md) |
| **LiveAPIDocs** | WebSocket Audio/Video Streaming | [`WebSocketStreaming.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/LiveAPIDocs/WebSocketStreaming.md) |
| **LiveAPIDocs** | Close Code 1007 & Critical Constraints | [`ConstraintsAndGotchas.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/LiveAPIDocs/ConstraintsAndGotchas.md) |
| **LiveAPIDocs** | Blind Visual Audit & A/B Convergence | [`VisualBlindAudit.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/LiveAPIDocs/VisualBlindAudit.md) |
| **VideoProductionDocs** | Golden Acting & Voice Production | [`GoldenActingStandard.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/VideoProductionDocs/GoldenActingStandard.md) |
| **PublishingDocs** | YouTube Semantic Category Selection | [`YouTubeSemanticCategories.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/PublishingDocs/YouTubeSemanticCategories.md) |
| **PublishingDocs** | Zero-Leak DB Sanitization | [`ZeroLeakSanitization.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/PublishingDocs/ZeroLeakSanitization.md) |

---

## How to Query & Reference
- When working on character movements or joint articulation, always check [`StickmanKinematics.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/DevDocs/StickmanKinematics.md) before writing angle code in `kinematic_presets.ts`.
- When developing or modifying Live API streaming connections, read [`ConstraintsAndGotchas.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/LiveAPIDocs/ConstraintsAndGotchas.md) to ensure proper WebSocket framing.
- When committing changes to `dev`, remember that the Zero-Leak hook automatically sanitizes databases as documented in [`ZeroLeakSanitization.md`](file:///d:/JerminaStudio/JerminaDev/docs/studio_knowledge/PublishingDocs/ZeroLeakSanitization.md).
