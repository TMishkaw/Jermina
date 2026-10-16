from pathlib import Path

from jemini.skills.skills_scout import SkillsScout


def test_skills_scout_discovery():
    scout = SkillsScout()
    skills = scout.list_installed_skills()

    skill_names = [s.name for s in skills]
    assert len(skills) >= 4
    assert "stickman-animation-composer" in skill_names
    assert "remotion-motion-designer" in skill_names


def test_skills_scout_creation_and_memory_export(tmp_path: Path):
    scout = SkillsScout(workspace_root=tmp_path)

    created_path = scout.create_skill(
        name="freesound-audio-fetcher",
        description="Automated CC0/Creative Commons sound effects search and download via Freesound API.",
        instructions="Use this skill to fetch whoosh, punch, laugh, and ambient SFX for video production.",
        scripts={"fetch_sfx.py": "# Freesound fetch script\nprint('fetching SFX...')\n"},
    )

    assert created_path.exists()
    content = created_path.read_text(encoding="utf-8")
    assert "name: freesound-audio-fetcher" in content

    # Test listing from tmp workspace
    skills = scout.list_installed_skills()
    assert len(skills) == 1
    assert skills[0].name == "freesound-audio-fetcher"
    assert skills[0].has_scripts is True

    # Test export to memory model
    memory_record = scout.export_skill_to_memory_record(skills[0])
    assert memory_record.category == "skill"
    assert memory_record.channel_id == "development_brain"
    assert "freesound-audio-fetcher" in memory_record.metadata_json["skill_name"]
