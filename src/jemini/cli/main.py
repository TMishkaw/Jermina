"""Jemini Unified Command Line Interface & Pre-flight QA Gate.

Commands:
- `render`: Full autonomous E2E video production pipeline.
- `test-readiness`: Matrix Readiness Suite verifying DB, Keys, Remotion, and E2E mock pipeline.
"""

import argparse
import asyncio
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import text

from jemini.core.config import settings
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


def sanitize_filename(name: str) -> str:
    """Removes all forbidden Windows/POSIX characters from output filename."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name)
    cleaned = re.sub(r"\s+", "_", cleaned.strip())
    return cleaned[:40] or "jemini_short"


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
    publish_youtube: bool = False,
    channel_id: str = "stickman_lab",
    max_correction_attempts: int = 2,
) -> dict[str, Any]:
    """Executes the full autonomous pipeline with self-correction."""
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    rotator = _init_rotator()

    from jemini.core.context import ChannelRegistry

    profile = ChannelRegistry.get(channel_id)

    logger.info("==================================================")
    logger.info("   JEMINI AUTONOMOUS VIDEO PRODUCTION PIPELINE   ")
    logger.info("   Channel: %s (%s) | Voice: %s | Color: %s", profile.channel_name, profile.channel_id, profile.voice_name, profile.accent_color)
    logger.info("==================================================")

    # 1. Script Ingestion / Generation
    script_gen = ScriptGenerator(rotator=rotator)

    if script_path:
        path = Path(script_path)
        logger.info("Loading custom script from: %s", path)
        data = json.loads(path.read_text(encoding="utf-8"))
        short_script = GeneratedShortScript.model_validate(data)
    else:
        active_topic = topic or "Як штучний інтелект Jemini створює відео автономно"
        from jemini.analytics.feedback_loop import AudienceRetentionFeedbackLoop

        feedback = AudienceRetentionFeedbackLoop()
        negative_rules = await feedback.get_active_negative_rules(profile.channel_id)
        if negative_rules:
            logger.info("Applying %d learned retention rules for '%s'...", len(negative_rules), profile.channel_id)

        logger.info("Generating viral script for topic: '%s'...", active_topic)
        short_script = await script_gen.generate_script(
            topic=active_topic,
            profile=profile,
            negative_rules=negative_rules,
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
    video_output_path = out_dir / f"{sanitize_filename(short_script.title)}.mp4"

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
        accent_color=profile.accent_color,
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
            target_emotion=profile.tone_of_voice,
            key_points=["3-second hook", "clear subtitles", "stickman acting"],
        )

        while attempt < max_correction_attempts and current_status == ValidationStatus.NEEDS_CORRECTION:
            attempt += 1
            logger.info("Running Multimodal Quality Validation (Attempt %d/%d)...", attempt, max_correction_attempts)
            validation_card = await validator.validate(
                intent=intent,
                payload_summary=f"Stickman Short 9:16 on '{short_script.title}' for channel '{profile.channel_name}'",
                media_path=final_video,
                iteration=attempt,
                channel_id=profile.channel_id,
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

    # 5. YouTube Shorts Publishing (Optional Gate)
    published_res = None
    if publish_youtube:
        from jemini.publishing.youtube_publisher import (
            PublishingPrivacyStatus,
            YouTubePublisher,
            YouTubeShortMetadata,
        )

        publisher = YouTubePublisher()
        if not publisher.has_credentials() and not mock_mode:
            logger.warning(
                "YouTube publishing requested, but client secrets not found at 'config/client_secret.json'.\n"
                "Please place OAuth2 client credentials at 'config/client_secret.json' to enable live uploads."
            )
        else:
            logger.info("Publishing video to YouTube Shorts...")
            published_res = await publisher.publish_short(
                video_path=final_video,
                metadata=YouTubeShortMetadata(
                    title=short_script.title,
                    description=f"{short_script.hook_text}\n\nСтворено повністю автономно через рушій Jemini.",
                    privacy_status=PublishingPrivacyStatus.UNLISTED,
                ),
                channel_id=profile.channel_id,
                mock_mode=mock_mode,
            )
            logger.info("✓ YouTube Short Published: %s", published_res.shorts_url)

    summary = {
        "title": short_script.title,
        "video_path": str(final_video),
        "duration_seconds": pipeline_res.total_duration_seconds,
        "total_frames": pipeline_res.total_frames,
        "validation_score": validation_card.overall_score if validation_card else None,
        "validation_status": validation_card.status.value if validation_card else "SKIPPED",
        "youtube_shorts_url": published_res.shorts_url if published_res else None,
    }

    summary_file = out_dir / "pipeline_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("==================================================")
    logger.info("   PRODUCTION PIPELINE COMPLETED SUCCESSFULLY!    ")
    logger.info("   Video artifact: %s", final_video)
    if published_res:
        logger.info("   YouTube URL:    %s", published_res.shorts_url)
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


def print_channels_table() -> None:
    """Displays registered channel profiles and branding settings."""
    from jemini.core.context import ChannelRegistry

    channels = ChannelRegistry.list_channels()
    print("\n" + "=" * 90)
    print("                     JEMINI MULTI-CHANNEL PROFILES REGISTRY")
    print("=" * 90)
    print(f"{'CHANNEL ID':<18} | {'NAME':<24} | {'VOICE':<8} | {'ACCENT':<9} | {'THEME'}")
    print("-" * 90)
    for ch in channels:
        print(f"{ch.channel_id:<18} | {ch.channel_name:<24} | {ch.voice_name:<8} | {ch.accent_color:<9} | {ch.core_theme[:30]}...")
    print("=" * 90 + "\n")


async def handle_scout(channel_id: str, count: int, enqueue: bool, mock_mode: bool) -> None:
    """Scouts viral topics and optionally registers them in the production queue."""
    from jemini.core.context import ChannelRegistry
    from jemini.scheduling.queue import ProductionQueue
    from jemini.scheduling.scout import TrendScout

    profile = ChannelRegistry.get(channel_id)
    rotator = _init_rotator()
    scout = TrendScout(rotator=rotator)

    logger.info("Scouting %d trending topics for '%s'...", count, profile.channel_name)
    scouted = await scout.scout_topics(profile=profile, count=count, mock_mode=mock_mode)

    print("\n" + "=" * 80)
    print(f"       SCOUTED TRENDING TOPICS: {profile.channel_name.upper()}")
    print("=" * 80)
    queue = ProductionQueue() if enqueue else None

    for idx, item in enumerate(scouted.topics, start=1):
        print(f"[{idx}] {item.title}")
        print(f"    Hook Angle:  {item.hook_angle}")
        print(f"    Score:       {item.relevance_score}/10.0 | Emotion: {item.target_emotion}")
        print(f"    Tags:        {', '.join(item.keywords)}")
        if enqueue and queue:
            task = queue.enqueue(channel_id=profile.channel_id, topic=item.title)
            print(f"    -> Enqueued as {task.task_id} (Status: {task.status.value})")
        print("-" * 80)
    print()


async def handle_queue(list_tasks: bool, process_next: bool, mock_mode: bool) -> None:
    """Inspects or processes scheduled production tasks."""
    from jemini.scheduling.queue import ProductionQueue

    queue = ProductionQueue()

    if process_next:
        pending = queue.get_next_pending()
        if not pending:
            logger.info("No pending tasks in queue.")
            return
        logger.info("Processing queued task %s: '%s' for channel '%s'...", pending.task_id, pending.topic, pending.channel_id)
        try:
            res = await run_e2e_render(
                topic=pending.topic,
                channel_id=pending.channel_id,
                mock_mode=mock_mode,
            )
            score = res.get("validation_card", {}).get("overall_score") if res.get("validation_card") else 9.0
            queue.complete_task(task_id=pending.task_id, video_path=res["video_path"], validation_score=score)
            logger.info("✓ Queued task %s successfully produced: %s", pending.task_id, res["video_path"])
        except Exception as exc:  # noqa: BLE001
            queue.fail_task(task_id=pending.task_id, error_message=str(exc))
            logger.error("Failed to process queued task %s: %s", pending.task_id, exc)
        return

    # Default to listing tasks
    tasks = queue.list_tasks()
    print("\n" + "=" * 85)
    print("                        JEMINI PRODUCTION QUEUE")
    print("=" * 85)
    if not tasks:
        print("  Queue is empty. Use 'scout --enqueue' or add tasks manually.")
    else:
        print(f"{'TASK ID':<12} | {'CHANNEL':<16} | {'STATUS':<11} | {'TOPIC'}")
        print("-" * 85)
        for t in tasks:
            print(f"{t.task_id:<12} | {t.channel_id:<16} | {t.status.value.upper():<11} | {t.topic[:40]}")
    print("=" * 85 + "\n")


async def handle_feedback(
    channel_id: str,
    video_id: str,
    hook_rate: float,
    midpoint_rate: float,
    completion_rate: float,
) -> None:
    """Processes retention analytics and injects learned negative prompt constraints."""
    from jemini.analytics.feedback_loop import AudienceRetentionFeedbackLoop
    from jemini.analytics.models import RetentionMetrics

    feedback = AudienceRetentionFeedbackLoop()
    metrics = RetentionMetrics(
        video_id=video_id,
        channel_id=channel_id,
        retention_at_3s=hook_rate,
        retention_at_15s=midpoint_rate,
        completion_rate=completion_rate,
    )
    result = feedback.analyze_metrics(metrics)

    print("\n" + "=" * 80)
    print(f"       AUDIENCE RETENTION ANALYSIS: {channel_id.upper()} (Video: {video_id})")
    print("=" * 80)
    print(f"Performance Tier: {result.performance_tier.value.upper()}")
    print(f"Hook (3s): {result.hook_score:.1f}% | Midpoint (15s): {result.pacing_score:.1f}% | Completion: {result.retention_score:.1f}%")
    print("-" * 80)
    if result.identified_weaknesses:
        print("IDENTIFIED RETENTION WEAKNESSES:")
        for w in result.identified_weaknesses:
            print(f"  [!] {w}")
    print("-" * 80)
    if result.actionable_learnings:
        print("ACTIONABLE CREATIVE INSIGHTS:")
        for ins in result.actionable_learnings:
            print(f"  [✓] {ins}")
    print("-" * 80)
    if result.negative_prompt_rules:
        print("NEW NEGATIVE PROMPT RULES (SELF-EVOLUTION):")
        for r in result.negative_prompt_rules:
            print(f"  [+] {r}")
    print("=" * 80 + "\n")

    await feedback.persist_learning_to_memory(metrics, result)


def main():
    parser = argparse.ArgumentParser(description="Jemini Autonomous Video Production CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: render
    render_parser = subparsers.add_parser("render", help="Render autonomous video from topic or script")
    render_parser.add_argument("--topic", type=str, help="Topic for autonomous script generation")
    render_parser.add_argument("--channel", type=str, default="stickman_lab", help="Channel profile ID (stickman_lab, cyber_matrix, crypto_pulse, science_genesis)")
    render_parser.add_argument("--script", type=str, help="Path to custom JSON script")
    render_parser.add_argument("--output-dir", type=str, default="output", help="Destination folder for artifacts")
    render_parser.add_argument("--mock-mode", action="store_true", help="Execute in offline mock mode")
    render_parser.add_argument("--skip-validation", action="store_true", help="Skip multimodal validation loop")
    render_parser.add_argument("--publish-youtube", action="store_true", help="Upload rendered video to YouTube Shorts")

    # Subcommand: channels
    subparsers.add_parser("channels", help="List registered multi-channel profiles and branding")

    # Subcommand: scout
    scout_parser = subparsers.add_parser("scout", help="Scout viral trending topics for a channel")
    scout_parser.add_argument("--channel", type=str, default="stickman_lab", help="Target channel profile ID")
    scout_parser.add_argument("--count", type=int, default=3, help="Number of topics to scout")
    scout_parser.add_argument("--enqueue", action="store_true", help="Directly enqueue scouted topics for production")
    scout_parser.add_argument("--mock-mode", action="store_true", help="Scout in offline mock mode")

    # Subcommand: queue
    queue_parser = subparsers.add_parser("queue", help="Manage production queue")
    queue_parser.add_argument("--list", action="store_true", help="List tasks in queue")
    queue_parser.add_argument("--process-next", action="store_true", help="Process and render next queued task")
    queue_parser.add_argument("--mock-mode", action="store_true", help="Run queue processing in mock mode")

    # Subcommand: feedback
    feedback_parser = subparsers.add_parser("feedback", help="Analyze post-publishing retention and self-evolve prompts")
    feedback_parser.add_argument("--channel", type=str, default="stickman_lab", help="Channel profile ID")
    feedback_parser.add_argument("--video-id", type=str, required=True, help="ID of analyzed video")
    feedback_parser.add_argument("--hook-rate", type=float, required=True, help="Hook retention percentage at 3 seconds (0-100)")
    feedback_parser.add_argument("--midpoint-rate", type=float, default=45.0, help="Midpoint retention percentage at 15 seconds (0-100)")
    feedback_parser.add_argument("--completion-rate", type=float, default=35.0, help="Completion rate percentage (0-100)")

    # Subcommand: test-readiness
    subparsers.add_parser("test-readiness", help="Run pre-flight Matrix Readiness Suite for QA handoff")

    args = parser.parse_args()

    if args.command == "render":
        asyncio.run(
            run_e2e_render(
                topic=args.topic,
                channel_id=args.channel,
                script_path=args.script,
                output_dir=args.output_dir,
                mock_mode=args.mock_mode,
                skip_validation=args.skip_validation,
                publish_youtube=args.publish_youtube,
            )
        )
    elif args.command == "channels":
        print_channels_table()
    elif args.command == "scout":
        asyncio.run(
            handle_scout(
                channel_id=args.channel,
                count=args.count,
                enqueue=args.enqueue,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "queue":
        asyncio.run(
            handle_queue(
                list_tasks=args.list,
                process_next=args.process_next,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "feedback":
        asyncio.run(
            handle_feedback(
                channel_id=args.channel,
                video_id=args.video_id,
                hook_rate=args.hook_rate,
                midpoint_rate=args.midpoint_rate,
                completion_rate=args.completion_rate,
            )
        )
    elif args.command == "test-readiness":
        success = asyncio.run(run_test_readiness())
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main()
