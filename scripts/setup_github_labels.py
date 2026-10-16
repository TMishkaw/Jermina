"""Script to initialize or sync standardized GitHub Labels for the Jemini project.

Supports execution via GitHub CLI (`gh label create`) or direct display.
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class GitHubLabel:
    name: str
    color: str
    description: str


LABELS: list[GitHubLabel] = [
    # 1. Type Labels
    GitHubLabel("type:defect-rca", "d73a4a", "Дефект/баг з обов'язковим RCA протоколом"),
    GitHubLabel("type:core-feature", "a2eeef", "Новий функціонал ядра або сервіс"),
    GitHubLabel("type:agent-hypothesis", "7057ff", "Автономна гіпотеза розвитку від AI-агента"),
    GitHubLabel("type:channel-onboard", "0075ca", "Реєстрація та налаштування нового каналу"),
    GitHubLabel("type:chore", "cfd3d7", "Технічний борг, залежності або рефакторинг"),
    # 2. Component Labels
    GitHubLabel("comp:core", "1d76db", "Ядро системи, контекст, моделі Pydantic"),
    GitHubLabel("comp:rotator", "f9d0c4", "Key Rotator та Hot Standby 429"),
    GitHubLabel("comp:voice-live", "b60205", "Gemini 3.8 Live WebSocket аудіо-рушій"),
    GitHubLabel("comp:remotion", "008672", "Remotion 9:16 відео, HUD, Stickman, VFX"),
    GitHubLabel("comp:database", "5319e7", "PostgreSQL, pgvector, схеми та міграції"),
    GitHubLabel("comp:publishing", "e99695", "YouTube Shorts Publisher, API платформ"),
    GitHubLabel("comp:analytics", "0e8a16", "Retention Feedback Loop, самонавчання"),
    GitHubLabel("comp:scheduling", "fbca04", "Trend Scout, черга генерації"),
    GitHubLabel("comp:operator", "c2e0c6", "Пульт модератора, Human-in-the-Loop"),
    GitHubLabel("comp:cli", "d4c5f9", "CLI інтерфейс, аргументи, E2E"),
    # 3. Channel Labels
    GitHubLabel("channel:stickman_lab", "00f0ff", "Канал Stickman Lab (#00F0FF)"),
    GitHubLabel("channel:cyber_matrix", "00ff66", "Канал Cyber Matrix (#00FF66)"),
    GitHubLabel("channel:crypto_pulse", "ffb800", "Канал Crypto Pulse (#FFB800)"),
    GitHubLabel("channel:science_genesis", "9d00ff", "Канал Science Genesis (#9D00FF)"),
    GitHubLabel("channel:global", "ffffff", "Загальний рівень для всіх каналів"),
    # 4. Priority Labels
    GitHubLabel("priority:blocker-p0", "b60205", "P0 Блокер: повний крах або критичний збій"),
    GitHubLabel("priority:high-p1", "d93f0b", "P1 Високий: блокує канал або сцену"),
    GitHubLabel("priority:medium-p2", "fbca04", "P2 Середній: стандартний пріоритет"),
    GitHubLabel("priority:low-p3", "0e8a16", "P3 Низький: другорядне завдання"),
    # 5. Origin Labels
    GitHubLabel("origin:human", "5319e7", "Створено людиною-розробником або оператором"),
    GitHubLabel("origin:agent-scout", "1d76db", "Створено автономним агентом Trend Scout"),
    GitHubLabel("origin:agent-retention", "0052cc", "Створено контуром Feedback Loop"),
    GitHubLabel("origin:virtual-art-director", "6f42c1", "Створено валідатором якості"),
]


def sync_labels(dry_run: bool = False) -> None:
    print(f"Jemini GitHub Labels Taxomony: {len(LABELS)} labels total.")
    for lbl in LABELS:
        if dry_run:
            print(f"[DRY RUN] Label: '{lbl.name}' | Color: #{lbl.color} | Desc: '{lbl.description}'")
            continue

        cmd = [
            "gh",
            "label",
            "create",
            lbl.name,
            "--color",
            lbl.color,
            "--description",
            lbl.description,
            "--force",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if res.returncode == 0:
                print(f"✓ Synced label: {lbl.name}")
            else:
                print(f"! Failed to sync {lbl.name}: {res.stderr.strip() or res.stdout.strip()}")
        except FileNotFoundError:
            print(
                "GitHub CLI ('gh') is not installed or not in PATH. Run with --export-json to export."
            )
            return


if __name__ == "__main__":
    if "--export-json" in sys.argv:
        print(
            json.dumps(
                [{"name": l.name, "color": l.color, "description": l.description} for l in LABELS],
                ensure_ascii=False,
                indent=2,
            )
        )
    elif "--dry-run" in sys.argv:
        sync_labels(dry_run=True)
    else:
        sync_labels(dry_run=False)
