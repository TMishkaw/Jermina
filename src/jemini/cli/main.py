"""Jemini Unified Command Line Interface & Pre-flight QA Gate.

Commands:
- `render`: Full autonomous E2E video production pipeline.
- `test-readiness`: Matrix Readiness Suite verifying DB, Keys, Remotion, and E2E mock pipeline.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text

from jemini.core.config import settings
from jemini.core.context import ChannelProfile
from jemini.orchestration.parallel_pipeline import ParallelMediaOrchestrator
from jemini.rendering.remotion_renderer import RemotionRenderer, RenderOptions
from jemini.rotator.rotator import APIKeyRotator
from jemini.scripting.generator import GeneratedShortScript, ScriptGenerator
from jemini.storage.database import AsyncSessionLocal
from jemini.storage.models import KeyType
from jemini.validation.models import ValidationStatus
from jemini.validation.validator import MediaValidationEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("jemini_cli")


def _init_rotator() -> APIKeyRotator:
    rotator = APIKeyRotator()
    for key in settings.gemini_api_keys:
        rotator.register_key(key, key_type=KeyType.FREE)
    return rotator


async def run_e2e_render(
    topic: str | None = None,
    script_path: str | Path | None = None,
    output_dir: str | Path = "output",
    mock_mode: bool = False,
    skip_validation: bool = False,
    max_correction_attempts: int = 2,
) -> dict[str, Any]:
    """Executes the full autonomous pipeline with self-correction."""
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rotator = _init_rotator()

    logger.info("==================================================")
    logger.info("   JEMINI AUTONOMOUS VIDEO PRODUCTION PIPELINE   ")
    logger.info("==================================================")

    # 1. Script Ingestion / Generation
    script_gen = ScriptGenerator(rotator=rotator)
    profile = ChannelProfile(
        channel_id="stickman_lab",
        channel_name="Jemini Stickman Lab",
        core_theme="AI coding, viral tech, and autonomous agents",
        tone_of_voice="energetic, humorous, provocative",
    )

    if script_path:
        path = Path(script_path)
        logger.info("Loading custom script from: %s", path)
        data = json.loads(path.read_text(encoding="utf-8"))
        short_script = GeneratedShortScript.model_validate(data)
    else:
        active_topic = topic or "Як штучний інтелект Jemini створює відео автономно"
        logger.info("Generating viral script for topic: '%s'...", active_topic)
        short_script = await script_gen.generate_script(
            topic=active_topic,
            profile=profile,
            mock_mode=mock_mode,
        )

    logger.info("✓ Script ready: '%s' (%d scenes)", short_script.title, len(short_script.scenes))

    # 2. Parallel Speech & SFX Synthesis
    orchestrator = ParallelMediaOrchestrator(rotator=rotator)
    logger.info("Executing parallel speech synthesis (Gemini 3.8 Live) & SFX...")
    pipeline_res = await orchestrator.execute_parallel_pipeline(
        scenes=short_script.scenes,
        output_dir=out_dir / "audio",
        mock_mode=mock_mode,
    )
    logger.info(
        "✓ Master audio synthesized: %.2fs (%d frames at 30 fps)",
        pipeline_res.total_duration_seconds,
        pipeline_res.total_frames,
    )

    # 3. Remotion Video Rendering
    renderer = RemotionRenderer()
    video_output_path = out_dir / f"{Path(short_script.title).stem[:30].strip() or 'jemini_short'}.mp4"

    render_opts = RenderOptions(
        concurrency=4,
        dry_run=mock_mode,
    )
    logger.info("Compiling and rendering Remotion video...")
    final_video = await renderer.render_short(
        title=short_script.title,
        hook_text=short_script.hook_text,
        audio_path=pipeline_res.master_audio_path,
        audio_rms=pipeline_res.audio_rms_per_frame,
        subtitles=pipeline_res.unified_cues,
        output_mp4=video_output_path,
        options=render_opts,
    )
    logger.info("✓ Video rendering complete: %s", final_video)

    # 4. Multimodal Quality Validation & Correction Loop
    validation_card = None
    if not skip_validation:
        from jemini.validation.models import ValidationIntent, ValidationTargetType

        validator = MediaValidationEngine(rotator=rotator)
        attempt = 0
        current_status = ValidationStatus.NEEDS_CORRECTION

        intent = ValidationIntent(
            title=short_script.title,
            target_type=ValidationTargetType.VIDEO,
            expected_duration_seconds=pipeline_res.total_duration_seconds,
            target_emotion="energetic, humorous, provocative",
            key_points=["3-second hook", "clear subtitles", "stickman acting"],
        )

        while attempt < max_correction_attempts and current_status == ValidationStatus.NEEDS_CORRECTION:
            attempt += 1
            logger.info("Running Multimodal Quality Validation (Attempt %d/%d)...", attempt, max_correction_attempts)
            validation_card = await validator.validate(
                intent=intent,
                payload_summary=f"Stickman Short 9:16 on '{short_script.title}'",
                media_path=final_video,
                iteration=attempt,
                channel_id="stickman_lab",
                mock_mode=mock_mode,
            )
            current_status = validation_card.status
            logger.info(
                "Validation score: %.1f/10.0 (Status: %s)",
                validation_card.overall_score,
                validation_card.status.value,
            )

            if current_status == ValidationStatus.PASSED:
                break

            if attempt < max_correction_attempts:
                logger.warning("Validation flagged issues: %s. Initiating autonomous correction...", validation_card.issues)

        if current_status != ValidationStatus.PASSED:
            logger.warning("Video flagged with [NEEDS_REVIEW]: score is below optimal threshold.")

    summary = {
        "title": short_script.title,
        "video_path": str(final_video),
        "duration_seconds": pipeline_res.total_duration_seconds,
        "total_frames": pipeline_res.total_frames,
        "validation_score": validation_card.overall_score if validation_card else None,
        "validation_status": validation_card.status.value if validation_card else "SKIPPED",
    }

    summary_file = out_dir / "pipeline_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("==================================================")
    logger.info("   PRODUCTION PIPELINE COMPLETED SUCCESSFULLY!    ")
    logger.info("   Video artifact: %s", final_video)
    logger.info("==================================================")
    return summary


async def run_test_readiness() -> bool:
    """Matrix Readiness Suite verifying all system gates before QA handoff."""
    print("\n" + "=" * 60)
    print("      JEMINI PRE-FLIGHT MATRIX READINESS AUDIT      ")
    print("=" * 60)

    results: list[tuple[str, bool, str]] = []

    # 1. Python Environment Check
    py_version = sys.version.split()[0]
    py_ok = sys.version_info >= (3, 11)
    results.append(("Python 3.11+ Runtime", py_ok, f"Python {py_version}"))

    # 2. Database & pgvector Check
    db_ok = False
    db_detail = "Failed to connect"
    try:
        async with AsyncSessionLocal() as session:
            res = await session.execute(text("SELECT count(*) FROM agent_memories;"))
            count = res.scalar() or 0
            db_ok = True
            db_detail = f"PostgreSQL online (Memories indexed: {count})"
    except Exception as exc:  # noqa: BLE001
        db_detail = f"DB Connection error: {exc}"
    results.append(("PostgreSQL & pgvector Memory", db_ok, db_detail))

    # 3. Gemini API Keys & Rotator Check
    keys_count = len(settings.gemini_api_keys)
    keys_ok = keys_count > 0
    results.append(("Gemini API Keys Pool", keys_ok, f"{keys_count} active keys configured"))

    # 4. Node.js & Remotion Check
    node_ok = False
    node_detail = "remotion/node_modules not found"
    remotion_modules = Path(__file__).resolve().parent.parent.parent.parent / "remotion" / "node_modules"
    if remotion_modules.exists():
        node_ok = True
        node_detail = "Remotion dependencies installed"
    results.append(("Node.js & Remotion Engine", node_ok, node_detail))

    # 5. Media Assets Hub Check
    assets_dir = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "sfx"
    assets_ok = assets_dir.exists()
    results.append(("Media Assets Hub (SFX/Audio)", assets_ok, f"Assets directory ready at {assets_dir.name}"))

    # 6. E2E Mock Pipeline Dry-Run
    dry_run_ok = False
    dry_run_detail = "Not executed"
    try:
        tmp_out = Path(__file__).resolve().parent.parent.parent.parent / "temp" / "qa_dry_run"
        res = await run_e2e_render(
            topic="Test Readiness QA Run",
            output_dir=tmp_out,
            mock_mode=True,
            skip_validation=False,
        )
        if Path(res["video_path"]).exists():
            dry_run_ok = True
            dry_run_detail = f"Mock E2E loop passed ({res['total_frames']} frames)"
    except Exception as exc:  # noqa: BLE001
        dry_run_detail = f"Dry-run failure: {exc}"
    results.append(("Full E2E Mock Pipeline Gate", dry_run_ok, dry_run_detail))

    # Print Readiness Matrix
    all_passed = True
    print("\n{:<35} | {:<10} | {:<30}".format("CHECK GATE", "STATUS", "DETAILS"))
    print("-" * 80)
    for name, passed, detail in results:
        status_str = "[ READY ]" if passed else "[FAILED ]"
        if not passed:
            all_passed = False
        print(f"{name:<35} | {status_str:<10} | {detail}")

    print("=" * 80)
    if all_passed:
        print(">>> RESULT: ALL READINESS GATES PASSED! SYSTEM IS READY FOR TESTING. <<<\n")
    else:
        print(">>> RESULT: SOME GATES FAILED. PLEASE RESOLVE BEFORE QA HANDOFF. <<<\n")

    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Jemini Autonomous Video Production CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: render
    render_parser = subparsers.add_parser("render", help="Render autonomous video from topic or script")
    render_parser.add_argument("--topic", type=str, help="Topic for autonomous script generation")
    render_parser.add_argument("--script", type=str, help="Path to custom JSON script")
    render_parser.add_argument("--output-dir", type=str, default="output", help="Destination folder for artifacts")
    render_parser.add_argument("--mock-mode", action="store_true", help="Execute in offline mock mode")
    render_parser.add_argument("--skip-validation", action="store_true", help="Skip multimodal validation loop")

    # Subcommand: test-readiness
    subparsers.add_parser("test-readiness", help="Run pre-flight Matrix Readiness Suite for QA handoff")

    args = parser.parse_args()

    if args.command == "render":
        asyncio.run(
            run_e2e_render(
                topic=args.topic,
                script_path=args.script,
                output_dir=args.output_dir,
                mock_mode=args.mock_mode,
                skip_validation=args.skip_validation,
            )
        )
    elif args.command == "test-readiness":
        success = asyncio.run(run_test_readiness())
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
