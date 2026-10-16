# Zero-Leak Policy & Automated Database Sanitization

## 1. Zero-Leak Principles
Under no circumstances may secrets, API keys, OAuth client secrets, or user tokens be committed to git repositories:
- `config/client_secret.json` is permanently git-ignored.
- Environment keys in `.env` are strictly excluded from source control.

---

## 2. Automated Git Pre-Commit Hook
Every `git commit` automatically triggers the pre-commit hook (`.git/hooks/pre-commit`):
1. Executes `jemini db-export` via [`pre_commit_export.py`](file:///d:/JerminaStudio/JerminaDev/scripts/pre_commit_export.py).
2. Sanitizes sensitive columns and blacklists authorization tables.
3. Serializes clean operational tables into `seeds/sanitized_db/`:
   - `agent_memories.json`
   - `stickman_motions.json`
   - `youtube_channels.json`
   - `youtube_videos.json`
   - `youtube_comments.json`
4. Ensures container restart immunity: in the event of Docker container destruction, all agent memory and evolved gestures are restored via `jemini db-restore`.
