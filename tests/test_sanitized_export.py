from pathlib import Path

import pytest

from jemini.storage.database import init_db
from jemini.storage.sanitized_export import (
    BLACKLISTED_TABLES,
    export_sanitized_db,
    restore_sanitized_db,
)


@pytest.mark.asyncio
async def test_sanitized_export_and_restore(tmp_path: Path):
    await init_db()
    export_dir = tmp_path / "sanitized_db"

    # 1. Test export
    summary = await export_sanitized_db(output_dir=export_dir)
    assert "stickman_motions" in summary
    assert "agent_memories" in summary
    assert "api_keys" not in summary  # STRICT Zero-Leak check!

    # Verify files created
    assert (export_dir / "stickman_motions.json").exists()
    assert (export_dir / "agent_memories.json").exists()
    assert not (export_dir / "api_keys.json").exists()

    # Verify no api keys leaked inside any exported file
    for json_file in export_dir.glob("*.json"):
        text = json_file.read_text(encoding="utf-8")
        assert "key_string" not in text
        assert "AIzaSy" not in text

    # 2. Test restore
    restore_summary = await restore_sanitized_db(input_dir=export_dir)
    assert restore_summary.get("stickman_motions", 0) >= 1
    assert restore_summary.get("agent_memories", 0) >= 1


def test_blacklist_policy():
    assert "api_keys" in BLACKLISTED_TABLES
