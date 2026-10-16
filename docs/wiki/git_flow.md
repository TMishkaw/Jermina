# Git Flow, Architecture Isolation & Zero-Leak Release Protocol

## 1. Branch Strategy & Hierarchy

```
[ main ] ◄────────────────────────────────── Stable Production Releases (Tagged vX.Y.Z)
   │
   └── [ dev ] ◄──────────────────────────── Active Integration & E2E Verification
          │
          ├── feature/stickman-motion-ab     Feature Branch (Short-lived, rebased)
          ├── fix/arm-kinematic-symmetry     Bugfix Branch (Linked to RCA Defect Issue)
          └── hypothesis/viral-hook-concept  Autonomous Agent Hypotheses
```

### 1.1 Branch Roles:
- **`main` (Production):** Protected. Never commit directly to `main`. Deploys to live channels only after Matrix Readiness passes.
- **`dev` (Integration):** Default working branch for all library improvements, PR merges, and pre-flight QA.
- **`feature/<name>`:** Discrete architectural enhancements or new components.
- **`fix/<defect-name>`:** Systemic fixes resolving verified RCA issues.
- **`hypothesis/<agent-id>`:** Autonomous agent explorations adhering to [`.github/ISSUE_TEMPLATE/03_agent_hypothesis.yml`](file:///d:/JerminaStudio/JerminaDev/.github/ISSUE_TEMPLATE/03_agent_hypothesis.yml).

---

## 2. Conventional Commits Standard
All git commits must strictly adhere to the Conventional Commits specification:

| Prefix | Meaning & Purpose | Example |
| :--- | :--- | :--- |
| `feat:` | New feature or capability | `feat(validation): implement isolated live motion auditor` |
| `fix:` | Defect resolution with root-cause elimination | `fix(kinematics): correct arm symmetry in shrug and explain poses` |
| `refactor:` | Code restructuring without functional changes | `refactor(rotator): streamline model cooldown timer evaluation` |
| `perf:` | Performance improvements (GPU, caching, memory) | `perf(remotion): enable bundle cache and concurrency 6` |
| `test:` | Adding or updating unit/integration tests | `test(publishing): add test suite for 31 YouTube categories` |
| `docs:` | Documentation updates or new specifications | `docs(mcp): expand YouTubeSemanticCategories to complete 31 categories` |
| `chore:` | Dependency bumps, CI scripts, pre-commit hooks | `chore(db): update sanitized PostgreSQL seeds` |

---

## 3. Automated Pre-Commit Hook (Zero-Leak Protocol)
- Located at `.git/hooks/pre-commit`.
- Automatically executes before every local commit:
  1. Runs [`scripts/pre_commit_export.py`](file:///d:/JerminaStudio/JerminaDev/scripts/pre_commit_export.py).
  2. Dumps sanitized operational knowledge into `seeds/sanitized_db/` (`stickman_motions.json`, `agent_memories.json`, `youtube_*.json`).
  3. Enforces zero secrets: `config/client_secret.json`, `.env`, and private tokens are strictly blocked from git staging.

---

## 4. Root-Cause First (RCA) Protocol for Pull Requests
Before submitting a PR to `dev`:
1. **Identify Root Cause:** Document why the architectural contract permitted the bug.
2. **Systemic Fix:** Update Pydantic models, base classes, or interfaces.
3. **Regression Lock:** Include a dedicated `pytest` reproducing the exact failure case.
4. **100% Test Green:** Ensure all `pytest tests/` pass before opening PR.
