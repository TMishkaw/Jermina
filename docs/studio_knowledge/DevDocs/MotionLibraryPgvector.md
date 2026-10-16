# Motion Library & Vector Memory Persistence

## 1. Architecture Overview
The stickman motion repository is managed via [`MotionLibraryManager`](file:///d:/JerminaStudio/JerminaDev/src/jemini/rendering/motion_library.py) and is architected to scale to thousands of kinematic gestures with sub-millisecond retrieval.

```
       [ Spoken Subtitle / Script Phrase ]
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
   [ Fast-Path: In-Memory ]   [ Deep Semantic Path: pgvector ]
   Keyword & stem exact match   gemini-embedding-2 (768-dim)
         │                           │
         └─────────────┬─────────────┘
                       ▼
            [ Resolved MotionSpec ]
         (animation, angles, eye, mouth, prop)
```

---

## 2. PostgreSQL Storage Schema (`stickman_motions`)
- **Table Name:** `stickman_motions`
- **Fields:**
  - `motion_id` (`VARCHAR(64)`, Primary Key): Unique identifier (e.g., `heart_hands_evolved`, `point_user`).
  - `category` (`VARCHAR(32)`): `core_gesture`, `evolved_gesture`, `situational`.
  - `intent_description` (`TEXT`): Full Ukrainian semantic description of the acting intent.
  - `keywords` (`JSONB` / Array): Fast in-memory lookup tokens.
  - `kinematic_spec` (`JSONB`): Precise joint angle parameters and facial expressions.
  - `embedding` (`VECTOR(768)`): pgvector dense representation generated via `gemini-embedding-2`.
  - `consecutive_wins` (`INTEGER`): Number of consecutive A/B convergence wins (minimum 2).
  - `evolution_notes` (`TEXT`): Rationale and evolutionary guidance from model evaluations.
  - `version` (`VARCHAR(16)`): Schema iteration (e.g. `v1.0`, `v2.0`).

---

## 3. Autonomous Evolution & Persistence Flow
1. When a new kinematic gesture is created or modified, it undergoes evaluation via [`LiveMotionAuditor`](file:///d:/JerminaStudio/JerminaDev/src/jemini/validation/live_motion_auditor.py).
2. The variant must achieve **2 consecutive wins** against the baseline in blind A/B testing.
3. Upon convergence, `MotionLibraryManager.register_ab_winner()`:
   - Updates the memory cache (`self._memory_cache`).
   - Flushes JSON dumps to `data/motions/motion_catalog.json` and `remotion/public/motions/motion_catalog.json`.
   - Generates embedding via `gemini-embedding-2` and commits to PostgreSQL.
4. The pre-commit hook automatically serializes the sanitized table into `seeds/sanitized_db/stickman_motions.json`.
