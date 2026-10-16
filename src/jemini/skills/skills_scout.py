"""Autonomous Skills Scout & Hub Engine.

Discovers, audits, generates, and indexes Antigravity SKILL.md modules
into PostgreSQL pgvector memory for dynamic agent tool retrieval.
"""

import logging
import re
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from jemini.storage.models import AgentMemory

logger = logging.getLogger(__name__)


class InstalledSkillMeta(BaseModel):
    name: str
    description: str
    path: str
    has_scripts: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class SkillsScout:
    """Manages the discovery, automated generation, and indexing of Antigravity skills."""

    def __init__(self, workspace_root: Path | str | None = None):
        base = Path(workspace_root) if workspace_root else Path(__file__).resolve().parent.parent.parent.parent
        self.workspace_root = base
        self.skills_dir = base / ".agents" / "skills"
        self.skills_dir.mkdir(parents=True, exist_ok=True)

    def _parse_frontmatter(self, file_content: str) -> tuple[dict[str, str], str]:
        """Parses YAML frontmatter between --- markers without external heavy YAML dependencies."""
        frontmatter = {}
        body = file_content
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", file_content, re.DOTALL)
        if match:
            raw_yaml, body = match.groups()
            for line in raw_yaml.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    frontmatter[key.strip()] = val.strip().strip("'\"")
        return frontmatter, body

    def list_installed_skills(self) -> list[InstalledSkillMeta]:
        """Discovers all valid skills in .agents/skills/ containing a SKILL.md."""
        installed = []
        if not self.skills_dir.exists():
            return installed

        for skill_folder in self.skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue
            skill_md = skill_folder / "SKILL.md"
            if skill_md.is_file():
                try:
                    text_data = skill_md.read_text(encoding="utf-8")
                    fm, _ = self._parse_frontmatter(text_data)
                    scripts_dir = skill_folder / "scripts"
                    has_scripts = scripts_dir.is_dir() and any(scripts_dir.iterdir())

                    installed.append(
                        InstalledSkillMeta(
                            name=fm.get("name", skill_folder.name),
                            description=fm.get("description", "No description provided."),
                            path=str(skill_md),
                            has_scripts=has_scripts,
                            metadata={"folder": skill_folder.name},
                        )
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("Failed to parse skill at %s: %s", skill_md, exc)

        return installed

    def create_skill(
        self,
        name: str,
        description: str,
        instructions: str,
        scripts: dict[str, str] | None = None,
        overwrite: bool = False
    ) -> Path:
        """Scaffolds a new Antigravity skill with standard SKILL.md and optional scripts."""
        clean_name = re.sub(r"[^a-zA-Z0-9_-]", "-", name.lower()).strip("-")
        target_dir = self.skills_dir / clean_name
        target_file = target_dir / "SKILL.md"

        if target_file.exists() and not overwrite:
            logger.info("Skill '%s' already exists at %s", clean_name, target_file)
            return target_file

        target_dir.mkdir(parents=True, exist_ok=True)

        content = (
            f"---\n"
            f"name: {clean_name}\n"
            f"description: {description.strip()}\n"
            f"---\n\n"
            f"# {clean_name.replace('-', ' ').title()} Skill\n\n"
            f"{instructions.strip()}\n"
        )
        target_file.write_text(content, encoding="utf-8")

        if scripts:
            scripts_dir = target_dir / "scripts"
            scripts_dir.mkdir(parents=True, exist_ok=True)
            for filename, script_code in scripts.items():
                (scripts_dir / filename).write_text(script_code, encoding="utf-8")

        logger.info("Successfully created skill '%s' at %s", clean_name, target_file)
        return target_file

    def export_skill_to_memory_record(self, meta: InstalledSkillMeta) -> AgentMemory:
        """Creates an AgentMemory model ready to be persisted into pgvector database."""
        content = f"## Skill: {meta.name}\n\n**Description:** {meta.description}\n\nPath: {meta.path}"
        return AgentMemory(
            channel_id="development_brain",
            category="skill",
            content=content,
            metadata_json={
                "skill_name": meta.name,
                "description": meta.description,
                "has_scripts": meta.has_scripts,
                "path": meta.path,
            }
        )
