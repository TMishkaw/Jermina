"""Pre-commit hook script to automatically export sanitized DB knowledge into Git."""

import asyncio
import subprocess
import sys

from jemini.storage.sanitized_export import export_sanitized_db


def stage_seeds():
    subprocess.run(["git", "add", "seeds/sanitized_db/"], check=True)


async def run_export():
    print("[pre-commit] Exporting sanitized DB knowledge (Zero-Leak)...")
    try:
        summary = await export_sanitized_db()
        print(f"[pre-commit] ✓ DB exported successfully: {summary}")
        stage_seeds()
    except Exception as exc:  # noqa: BLE001
        print(f"[pre-commit] Warning: DB export failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(run_export())
