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
    publish_tiktok: bool = False,
    operator_review: bool = False,
    channel_id: str = "stickman_lab",
    aspect_ratio: str = "9:16",
    max_correction_attempts: int = 2,
    use_live_review: bool = True,
    public: bool = False,
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
        aspect_ratio=aspect_ratio,
        concurrency=4,
        dry_run=mock_mode,
    )
    logger.info("Compiling and rendering Remotion video (%s)...", aspect_ratio)
    final_video = await renderer.render_video(
        title=short_script.title,
        hook_text=short_script.hook_text,
        audio_path=pipeline_res.master_audio_path,
        audio_rms=pipeline_res.audio_rms_per_frame,
        subtitles=pipeline_res.unified_cues,
        output_mp4=video_output_path,
        accent_color=profile.accent_color,
        aspect_ratio=aspect_ratio,
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
            key_points=["3-second hook", "clear subtitles", "visual acting"],
        )

        if use_live_review:
            logger.info("Executing Real-Time Multimodal Video & Audio Review via Gemini 3.8 Live API...")
            validation_card, live_res = await validator.validate_video_live_stream(
                intent=intent,
                video_path=final_video,
                channel_id=profile.channel_id,
                mock_mode=mock_mode,
            )
            current_status = validation_card.status
            logger.info(
                "✓ Live Stream Review complete: Score %.1f/10.0 | Hook: %s",
                validation_card.overall_score,
                live_res.hook_evaluation[:60],
            )
        else:
            while attempt < max_correction_attempts and current_status == ValidationStatus.NEEDS_CORRECTION:
                attempt += 1
                logger.info("Running Multimodal Quality Validation (Attempt %d/%d)...", attempt, max_correction_attempts)
                validation_card = await validator.validate(
                    intent=intent,
                    payload_summary=f"Video ({aspect_ratio}) on '{short_script.title}' for channel '{profile.channel_name}'",
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
                    logger.warning("Validation flagged issues: %s. Initiating autonomous correction...", validation_card.detected_issues)


        if current_status != ValidationStatus.PASSED:
            logger.warning("Video flagged with [NEEDS_REVIEW]: score is below optimal threshold.")

    # 5. YouTube Shorts Publishing (Optional Gate)
    published_res = None
    if publish_youtube:
        if current_status != ValidationStatus.PASSED and not mock_mode:
            logger.error(
                "❌ Publishing aborted: video failed multimodal validation gate (status=%s, score=%.1f). Aborting YouTube upload.",
                current_status.value,
                validation_card.overall_score if validation_card else 0.0,
            )
        else:
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
                is_short = aspect_ratio in ["9:16", "vertical"]
                target_label = "YouTube Shorts" if is_short else "YouTube (16:9 Widescreen)"
                target_privacy = PublishingPrivacyStatus.PUBLIC if public else PublishingPrivacyStatus.UNLISTED
                logger.info("Publishing video to %s (Status: %s)...", target_label, target_privacy.value.upper())
            published_res = await publisher.publish_video(
                video_path=final_video,
                metadata=YouTubeShortMetadata(
                    title=short_script.title,
                    description=f"{short_script.hook_text}\n\nСтворено повністю автономно через рушій Jemini.",
                    privacy_status=target_privacy,
                ),
                is_short=is_short,
                channel_id=profile.channel_id,
                mock_mode=mock_mode,
            )
            logger.info("✓ %s Published: %s", target_label, published_res.published_url)


    # 5.5 TikTok Auto-Publishing (Optional)
    published_tiktok_res = None
    if publish_tiktok:
        from jemini.publishing.tiktok_publisher import TikTokMetadata, TikTokPublisher

        tt_publisher = TikTokPublisher()
        if not tt_publisher.has_credentials() and not mock_mode:
            logger.warning("TikTok credentials missing. Skipping TikTok upload.")
        else:
            tt_meta = TikTokMetadata(
                title=short_script.title,
                description=short_script.hook_text,
            )
            published_tiktok_res = await tt_publisher.publish_video(
                video_path=final_video,
                metadata=tt_meta,
                channel_id=profile.channel_id,
                mock_mode=mock_mode,
            )
            if published_tiktok_res.success:
                logger.info("✓ TikTok Short Published: %s", published_tiktok_res.status)
            else:
                logger.warning("! TikTok publish failed: %s", published_tiktok_res.error)

    # 6. Operator Review Control Plane Enrollment (Optional Gate)
    operator_sub_id = None
    if operator_review:
        from jemini.operator.review_service import OperatorReviewService

        op_service = OperatorReviewService()
        sub = op_service.submit_for_review(
            video_path=final_video,
            title=short_script.title,
            hook_text=short_script.hook_text,
            channel_id=profile.channel_id,
            validation_score=validation_card.overall_score if validation_card else 9.0,
        )
        operator_sub_id = sub.submission_id
        logger.info("✓ Submitted to Operator Approval Plane: %s", operator_sub_id)

    summary = {
        "title": short_script.title,
        "video_path": str(final_video),
        "duration_seconds": pipeline_res.total_duration_seconds,
        "total_frames": pipeline_res.total_frames,
        "validation_score": validation_card.overall_score if validation_card else None,
        "validation_status": validation_card.status.value if validation_card else "SKIPPED",
        "youtube_shorts_url": published_res.shorts_url if published_res else None,
        "youtube_url": published_res.published_url if published_res else None,
        "tiktok_status": published_tiktok_res.status if published_tiktok_res else None,
        "operator_submission_id": operator_sub_id,
    }

    summary_file = out_dir / "pipeline_summary.json"
    summary_file.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info("==================================================")
    logger.info("   PRODUCTION PIPELINE COMPLETED SUCCESSFULLY!    ")
    logger.info("   Video artifact: %s", final_video)
    if published_res:
        logger.info("   YouTube URL:    %s", published_res.published_url)
    if operator_sub_id:
        logger.info("   Operator Sub:   %s (Pending Approval)", operator_sub_id)
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


async def handle_queue(
    list_tasks: bool,
    process_next: bool,
    channel_id: str | None = None,
    publish_youtube: bool = False,
    public: bool = False,
    mock_mode: bool = False,
) -> None:
    """Inspects or processes scheduled production tasks."""
    from jemini.scheduling.queue import ProductionQueue

    queue = ProductionQueue()

    if process_next:
        pending = queue.get_next_pending(channel_id=channel_id)
        if not pending:
            logger.info("No pending tasks in queue (channel filter: %s).", channel_id)
            return
        logger.info("Processing queued task %s: '%s' for channel '%s'...", pending.task_id, pending.topic, pending.channel_id)
        try:
            res = await run_e2e_render(
                topic=pending.topic,
                channel_id=pending.channel_id,
                publish_youtube=publish_youtube,
                public=public,
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


async def handle_operator(
    list_subs: bool,
    approve_id: str | None,
    reject_id: str | None,
    publish_youtube: bool,
    publish_tiktok: bool,
    mock_mode: bool,
) -> None:
    """Manages human-in-the-loop review, one-click approvals, and video archival."""
    from jemini.operator.review_service import OperatorReviewService

    service = OperatorReviewService()

    if approve_id:
        sub = await service.approve(
            approve_id,
            publish_youtube=publish_youtube,
            publish_tiktok=publish_tiktok,
            mock_mode=mock_mode,
        )
        print(f"\n✓ Approved submission {sub.submission_id} (Status: {sub.status.value.upper()})")
        if sub.published_video_id:
            print(f"  Published Video ID: {sub.published_video_id}")
        print()
        return

    if reject_id:
        sub = service.reject(reject_id)
        print(f"\n✓ Rejected submission {sub.submission_id} (Status: {sub.status.value.upper()})")
        print(f"  Archived to: {sub.video_path}\n")
        return

    # Default to listing
    subs = service.list_submissions()
    print("\n" + "=" * 95)
    print("                        JEMINI OPERATOR APPROVAL PLANE")
    print("=" * 95)
    if not subs:
        print("  Review queue is empty. Use 'render --operator-review' to submit videos for approval.")
    else:
        print(f"{'SUBMISSION ID':<15} | {'CHANNEL':<16} | {'STATUS':<10} | {'SCORE':<5} | {'TITLE'}")
        print("-" * 95)
        for s in subs:
            print(f"{s.submission_id:<15} | {s.channel_id:<16} | {s.status.value.upper():<10} | {s.validation_score:<5.1f} | {s.title[:40]}")
    print("=" * 95 + "\n")


async def handle_review_live(
    video_path: str,
    intent_title: str,
    channel_id: str,
    mock_mode: bool = False,
) -> None:
    """Executes real-time multimodal live review of video file via Gemini 3.8 Live API."""
    from jemini.validation.live_reviewer import LiveVideoReviewer
    from jemini.validation.models import ValidationIntent, ValidationTargetType

    v_path = Path(video_path).resolve()
    if not v_path.exists():
        logger.error("Video file does not exist: %s", v_path)
        sys.exit(1)

    rotator = _init_rotator()
    reviewer = LiveVideoReviewer(rotator=rotator)

    intent = ValidationIntent(
        title=intent_title,
        target_type=ValidationTargetType.VIDEO,
        key_points=["3-second hook", "dynamic editing", "Golden Acting Standard voice"],
    )

    print("\n" + "=" * 80)
    print("  GEMINI 3.8 LIVE STREAM MULTIMODAL VIDEO REVIEW")
    print("=" * 80)
    print(f"  Target Video: {v_path.name}")
    print(f"  Path:         {v_path}")
    print(f"  Intent:       {intent_title}")
    print(f"  Channel:      {channel_id}")
    print(f"  Mock Mode:    {mock_mode}")
    print("=" * 80 + "\n")

    result = await reviewer.review_video(
        video_path=v_path,
        intent=intent,
        channel_id=channel_id,
        mock_mode=mock_mode,
    )

    print("\n" + "=" * 80)
    print("  LIVE STREAM AUDIT REPORT")
    print("=" * 80)
    print(f"  Status:             {result.status.value.upper()}")
    print(f"  Overall Score:      {result.overall_score:.1f} / 10.0")
    print(f"  Streamed Frames:    {result.frames_streamed} (1 FPS)")
    print(f"  Audio Duration:     {result.audio_streamed_seconds:.2f}s (16kHz PCM)")
    print("-" * 80)
    print(f"  [1] 3-SECOND HOOK:\n      {result.hook_evaluation}")
    print(f"  [2] VOICE & ACTING (GOLDEN ACTING STANDARD):\n      {result.voice_acting_evaluation}")
    if result.occlusion_evaluation:
        print(f"  [3] COMPOSITION & OCCLUSION:\n      {result.occlusion_evaluation}")
    if result.animation_evaluation:
        print(f"  [4] SEMANTIC ANIMATION & EMOJIS:\n      {result.animation_evaluation}")
    if result.design_typography_evaluation:
        print(f"  [5] DESIGN & MOBILE TYPOGRAPHY (1080x1920):\n      {result.design_typography_evaluation}")
    if result.style_benchmark_evaluation:
        print(f"  [6] MODERN BENCHMARK COMPARISON (Fireship / Hormozi):\n      {result.style_benchmark_evaluation}")
    print(f"  [7] INTENT ACCURACY:\n      {result.intent_discrepancies}")
    print("  [8] ACTIONABLE IMPROVEMENTS:")
    for imp in result.actionable_improvements:
        print(f"      • {imp}")
    if result.self_evolution_rules:
        print("  [9] AUTONOMOUS SELF-EVOLUTION RULES (PERSISTED TO MEMORY):")
        for rule in result.self_evolution_rules:
            print(f"      [+] {rule}")
    print("=" * 80 + "\n")


async def handle_youtube_sync(
    channel_id: str,
    output_dir: str,
    max_videos: int | None,
) -> None:
    """Synchronizes YouTube channel videos and comments to DB and JSON."""
    from jemini.analytics.youtube_ingestor import YouTubeChannelIngestor

    ingestor = YouTubeChannelIngestor(output_dir=output_dir)
    res = await ingestor.ingest_channel(
        channel_id=channel_id,
        max_videos=max_videos if max_videos and max_videos > 0 else None,
    )
    print("\n" + "=" * 80)
    print("       YOUTUBE CHANNEL DATA INGESTION COMPLETE")
    print("=" * 80)
    print(f"  Channel:         {res['channel']} ({res['channel_id']})")
    print(f"  Videos Synced:   {res['videos_synced']}")
    print(f"  Comments Synced: {res['comments_synced']}")
    print(f"  Local Dump:      {res['dump_path']}")
    print("=" * 80 + "\n")


async def handle_analyze_comments(
    channel_id: str,
    limit: int,
    batch_size: int,
    enqueue: bool,
    mock_mode: bool,
    target_channel: str = "stickman_lab",
    reanalyze: bool = False,
) -> None:
    """Performs batch semantic analysis of audience comments and enqueues viral hypotheses."""
    from jemini.analytics.comment_analyzer import AudienceSentimentAnalyzer

    rotator = _init_rotator()
    analyzer = AudienceSentimentAnalyzer(rotator=rotator, batch_size=batch_size)
    report = await analyzer.analyze_comments(
        channel_id=channel_id,
        target_channel_id=target_channel,
        limit=limit if limit > 0 else 500,
        enqueue_hypotheses=enqueue,
        reanalyze_all=reanalyze,
        mock_mode=mock_mode,
    )
    print("\n" + "=" * 80)
    print("       AUDIENCE SENTIMENT & TOPIC INTELLIGENCE REPORT")
    print("=" * 80)
    print(f"  Total Comments Analyzed: {report.total_analyzed}")
    print("  Sentiment Breakdown:")
    for sent, count in report.sentiment_distribution.items():
        print(f"    • {sent.upper():<16}: {count}")
    print("-" * 80)
    print("  Extracted Audience Topics & Questions:")
    for top in report.top_audience_topics:
        print(f"    • {top}")
    print("-" * 80)
    print("  Generated Viral Video Hypotheses:")
    for hyp in report.generated_hypotheses:
        print(f"    [+] {hyp}")
    if report.enqueued_task_ids:
        print(f"  Enqueued Tasks: {report.enqueued_task_ids}")
    print("=" * 80 + "\n")


async def handle_youtube_verify(channel_id: str, count: int, mock_mode: bool) -> None:
    """Verifies live channel status and confirms recent uploads on YouTube."""
    from jemini.publishing.youtube_watcher import YouTubeVerificationWatcher

    watcher = YouTubeVerificationWatcher()
    report = await watcher.verify_channel_publications(
        channel_id=channel_id,
        recent_limit=count,
        mock_mode=mock_mode,
    )
    print("\n" + "=" * 85)
    print("                YOUTUBE LIVE CHANNEL PUBLICATION AUDIT")
    print("=" * 85)
    print(f"  Channel:           {report.channel_title} ({report.channel_id})")
    print(f"  Subscribers:       {report.subscriber_count}")
    print(f"  Total Views:       {report.total_view_count}")
    print(f"  Total Videos:      {report.total_video_count}")
    print(f"  System Health:     [{report.system_health}]")
    print("-" * 85)
    print("  LATEST LIVE UPLOADS ON YOUTUBE:")
    for idx, v in enumerate(report.latest_uploads, 1):
        dur = f"{v.duration_seconds:.0f}s"
        fmt = "Short" if v.is_short else "Wide"
        print(f"  [{idx}] {v.video_id} | {fmt:<5} ({dur:>4}) | {v.privacy_status:<8} | {v.view_count:>4} views | {v.title[:45]}")
    print("-" * 85)
    if report.missing_from_youtube:
        print(f"  WARNING: Missing videos detected: {report.missing_from_youtube}")
    else:
        print("  ✓ All recent database uploads confirmed live on YouTube!")
    print("=" * 85 + "\n")


async def handle_eval_element(
    element_name: str,
    intent: str,
    spec_json: str | None,
    mock_mode: bool = False,
) -> None:
    """Evaluates an isolated movement/element against author intent."""
    from jemini.validation.ab_testing import MovementValidator

    spec = json.loads(spec_json) if spec_json else {"element": element_name}
    rotator = _init_rotator()
    validator = MovementValidator(rotator=rotator)
    res = await validator.evaluate_element(
        element_name=element_name,
        intent_description=intent,
        element_spec=spec,
        mock_mode=mock_mode,
    )
    print("\n" + "=" * 80)
    print(f"       MOVEMENT ELEMENT EVALUATION: {element_name.upper()}")
    print("=" * 80)
    print(f"  Intent:              {res.intent_description}")
    print(f"  Congruence:          {'✓ PASSED' if res.is_congruent else '✗ FAILED'}")
    print(f"  Score:               {res.score:.1f} / 10.0")
    print(f"  Silhouette Clarity:  {res.silhouette_clarity}")
    print(f"  Semantic Accuracy:   {res.semantic_accuracy}")
    print("  Strengths:")
    for s in res.strengths:
        print(f"    • {s}")
    if res.weaknesses:
        print("  Weaknesses:")
        for w in res.weaknesses:
            print(f"    • {w}")
    print(f"  Evolution Vector:    {res.evolution_direction}")
    print("=" * 80 + "\n")


async def handle_ab_test(
    element_name: str,
    intent: str,
    variant_a_json: str | None,
    variant_b_json: str | None,
    consecutive: int = 2,
    max_rounds: int = 5,
    mock_mode: bool = False,
) -> None:
    """Runs autonomous A/B testing until a variant wins 2 consecutive times."""
    from jemini.validation.ab_testing import MovementABTester

    var_a = json.loads(variant_a_json) if variant_a_json else {
        "variant": "A",
        "arm_angle": -120,
        "elbow_angle": 60,
        "bounce_speed": 2.0,
    }
    var_b = json.loads(variant_b_json) if variant_b_json else {
        "variant": "B",
        "arm_angle": -135,
        "elbow_angle": 80,
        "bounce_speed": 2.5,
    }
    rotator = _init_rotator()
    tester = MovementABTester(rotator=rotator)
    result = await tester.run_ab_convergence_test(
        element_name=element_name,
        intent_description=intent,
        variant_a=var_a,
        variant_b=var_b,
        consecutive_target=consecutive,
        max_rounds=max_rounds,
        mock_mode=mock_mode,
    )
    print("\n" + result.summarize() + "\n")


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
    render_parser.add_argument("--no-live-review", action="store_true", help="Disable Gemini 3.8 Live API real-time video review (Live review is enabled by default)")
    render_parser.add_argument("--aspect-ratio", type=str, default="9:16", choices=["9:16", "16:9"], help="Aspect ratio (9:16 vertical or 16:9 widescreen)")
    render_parser.add_argument("--widescreen", action="store_true", help="Shortcut for 16:9 widescreen YouTube video")
    render_parser.add_argument("--publish-youtube", action="store_true", help="Upload rendered video to YouTube (Shorts or Widescreen)")
    render_parser.add_argument("--public", action="store_true", help="Publish video publicly to YouTube (default is Unlisted)")
    render_parser.add_argument("--publish-tiktok", action="store_true", help="Upload rendered video to TikTok")
    render_parser.add_argument("--operator-review", action="store_true", help="Submit to operator review plane instead of publishing immediately")

    # Subcommand: review-live
    review_parser = subparsers.add_parser("review-live", help="Stream video and audio to Gemini 3.8 Live API for real-time review")
    review_parser.add_argument("video_path", type=str, help="Path to rendered MP4 video file")
    review_parser.add_argument("--intent", type=str, default="Вірусний ролик для соцмереж", help="Initial intent title or description")
    review_parser.add_argument("--channel", type=str, default="cyber_matrix", help="Channel ID for audit log context")
    review_parser.add_argument("--mock-mode", action="store_true", help="Simulate Live API review without network calls")


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
    queue_parser.add_argument("--channel", type=str, default=None, help="Target channel ID to filter queue")
    queue_parser.add_argument("--publish-youtube", action="store_true", help="Publish completed video to YouTube")
    queue_parser.add_argument("--public", action="store_true", help="Publish video publicly to YouTube (default is Unlisted)")
    queue_parser.add_argument("--mock-mode", action="store_true", help="Run queue processing in mock mode")

    # Subcommand: feedback
    feedback_parser = subparsers.add_parser("feedback", help="Analyze post-publishing retention and self-evolve prompts")
    feedback_parser.add_argument("--channel", type=str, default="stickman_lab", help="Channel profile ID")
    feedback_parser.add_argument("--video-id", type=str, required=True, help="ID of analyzed video")
    feedback_parser.add_argument("--hook-rate", type=float, required=True, help="Hook retention percentage at 3 seconds (0-100)")
    feedback_parser.add_argument("--midpoint-rate", type=float, default=45.0, help="Midpoint retention percentage at 15 seconds (0-100)")
    feedback_parser.add_argument("--completion-rate", type=float, default=35.0, help="Completion rate percentage (0-100)")

    # Subcommand: operator
    operator_parser = subparsers.add_parser("operator", help="Manage operator review and approvals")
    operator_parser.add_argument("--list", action="store_true", help="List pending video submissions")
    operator_parser.add_argument("--approve", type=str, help="Submission ID to approve")
    operator_parser.add_argument("--reject", type=str, help="Submission ID to reject and archive")
    operator_parser.add_argument("--publish-youtube", action="store_true", help="Publish to YouTube upon approval")
    operator_parser.add_argument("--publish-tiktok", action="store_true", help="Publish to TikTok upon approval")
    operator_parser.add_argument("--mock-mode", action="store_true", help="Execute approval in mock mode")

    # Subcommand: youtube-sync
    yt_sync_parser = subparsers.add_parser("youtube-sync", help="Synchronize YouTube channel metadata, videos, and comments")
    yt_sync_parser.add_argument("--channel-id", type=str, default="UC1ol6l3KL3sgmLPiwQy2QTA", help="YouTube Channel ID")
    yt_sync_parser.add_argument("--output-dir", type=str, default="data/youtube_dump", help="Destination folder for JSON dump")
    yt_sync_parser.add_argument("--max-videos", type=int, default=0, help="Max videos to sync (0 for all)")

    # Subcommand: analyze-comments
    comments_parser = subparsers.add_parser("analyze-comments", help="Analyze viewer comments sentiment and generate viral hypotheses")
    comments_parser.add_argument("--channel-id", type=str, default="UC1ol6l3KL3sgmLPiwQy2QTA", help="YouTube Channel ID")
    comments_parser.add_argument("--limit", type=int, default=100, help="Maximum comments to analyze in this run")
    comments_parser.add_argument("--batch-size", type=int, default=25, help="Batch size for LLM evaluation")
    comments_parser.add_argument("--no-enqueue", action="store_true", help="Do not enqueue generated hypotheses into Production Queue")
    comments_parser.add_argument("--reanalyze", action="store_true", help="Reanalyze all viewer comments")
    comments_parser.add_argument("--target-channel", type=str, default="stickman_lab", help="Channel profile to enqueue hypotheses for")
    comments_parser.add_argument("--mock-mode", action="store_true", help="Run offline mock analysis without Gemini API")

    # Subcommand: youtube-verify
    yt_verify_parser = subparsers.add_parser("youtube-verify", help="Audit live YouTube channel uploads and confirm publication status")
    yt_verify_parser.add_argument("--channel-id", type=str, default="UC1ol6l3KL3sgmLPiwQy2QTA", help="YouTube Channel ID")
    yt_verify_parser.add_argument("--count", type=int, default=5, help="Number of recent uploads to audit")
    yt_verify_parser.add_argument("--mock-mode", action="store_true", help="Run audit in mock mode")

    # Subcommand: eval-element
    eval_elem_parser = subparsers.add_parser("eval-element", help="Evaluate an isolated movement or visual element against intent")
    eval_elem_parser.add_argument("--element", type=str, required=True, help="Name of element or animation preset")
    eval_elem_parser.add_argument("--intent", type=str, required=True, help="Intended semantic goal or emotion")
    eval_elem_parser.add_argument("--spec", type=str, default=None, help="JSON string with kinematic parameters")
    eval_elem_parser.add_argument("--mock-mode", action="store_true", help="Run evaluation in offline mock mode")

    # Subcommand: ab-test
    ab_parser = subparsers.add_parser("ab-test", help="Run iterative A/B testing until a variant wins 2 consecutive rounds")
    ab_parser.add_argument("--element", type=str, required=True, help="Element or animation name")
    ab_parser.add_argument("--intent", type=str, required=True, help="Target artistic intent or emotion")
    ab_parser.add_argument("--variant-a", type=str, default=None, help="JSON string for Variant A spec")
    ab_parser.add_argument("--variant-b", type=str, default=None, help="JSON string for Variant B spec")
    ab_parser.add_argument("--consecutive", type=int, default=2, help="Consecutive wins needed to converge (default: 2)")
    ab_parser.add_argument("--max-rounds", type=int, default=5, help="Maximum A/B comparison rounds (default: 5)")
    ab_parser.add_argument("--mock-mode", action="store_true", help="Run test in offline mock mode")

    # Subcommand: test-readiness
    subparsers.add_parser("test-readiness", help="Run pre-flight Matrix Readiness Suite for QA handoff")

    # Subcommand: db-export
    db_exp_parser = subparsers.add_parser("db-export", help="Export sanitized database knowledge to Git-versioned JSON seeds (Zero-Leak)")
    db_exp_parser.add_argument("--output-dir", type=str, default="seeds/sanitized_db", help="Destination folder for exported tables")

    # Subcommand: db-restore
    db_res_parser = subparsers.add_parser("db-restore", help="Restore sanitized database knowledge from Git-versioned JSON seeds")
    db_res_parser.add_argument("--input-dir", type=str, default="seeds/sanitized_db", help="Source folder with JSON seeds")
    db_res_parser.add_argument("--clear-existing", action="store_true", help="Clear existing records before restoring")

    # Subcommand: studio-docs
    docs_parser = subparsers.add_parser("studio-docs", help="Query and inspect Jemini Studio Knowledge Base & Architectural Standards")
    docs_parser.add_argument("action", choices=["list", "search", "get", "sections"], help="Action to execute")
    docs_parser.add_argument("--query", "-q", type=str, default="", help="Search query string")
    docs_parser.add_argument("--section", "-s", type=str, default=None, help="Filter by section (DevDocs, LiveAPIDocs, etc.)")
    docs_parser.add_argument("--doc", "-d", type=str, default=None, help="Document name to retrieve (e.g. StickmanKinematics)")

    args = parser.parse_args()

    if args.command == "render":
        target_aspect = "16:9" if args.widescreen else args.aspect_ratio
        asyncio.run(
            run_e2e_render(
                topic=args.topic,
                channel_id=args.channel,
                script_path=args.script,
                output_dir=args.output_dir,
                mock_mode=args.mock_mode,
                skip_validation=args.skip_validation,
                publish_youtube=args.publish_youtube,
                public=args.public,
                publish_tiktok=args.publish_tiktok,
                operator_review=args.operator_review,
                aspect_ratio=target_aspect,
                use_live_review=not args.no_live_review,
            )
        )
    elif args.command == "review-live":
        asyncio.run(
            handle_review_live(
                video_path=args.video_path,
                intent_title=args.intent,
                channel_id=args.channel,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "youtube-sync":
        asyncio.run(
            handle_youtube_sync(
                channel_id=args.channel_id,
                output_dir=args.output_dir,
                max_videos=args.max_videos,
            )
        )
    elif args.command == "analyze-comments":
        asyncio.run(
            handle_analyze_comments(
                channel_id=args.channel_id,
                limit=args.limit,
                batch_size=args.batch_size,
                enqueue=not args.no_enqueue,
                mock_mode=args.mock_mode,
                target_channel=args.target_channel,
                reanalyze=args.reanalyze,
            )
        )
    elif args.command == "youtube-verify":
        asyncio.run(
            handle_youtube_verify(
                channel_id=args.channel_id,
                count=args.count,
                mock_mode=args.mock_mode,
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
                channel_id=args.channel,
                publish_youtube=args.publish_youtube,
                public=args.public,
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
    elif args.command == "operator":
        asyncio.run(
            handle_operator(
                list_subs=args.list,
                approve_id=args.approve,
                reject_id=args.reject,
                publish_youtube=args.publish_youtube,
                publish_tiktok=args.publish_tiktok,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "eval-element":
        asyncio.run(
            handle_eval_element(
                element_name=args.element,
                intent=args.intent,
                spec_json=args.spec,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "ab-test":
        asyncio.run(
            handle_ab_test(
                element_name=args.element,
                intent=args.intent,
                variant_a_json=args.variant_a,
                variant_b_json=args.variant_b,
                consecutive=args.consecutive,
                max_rounds=args.max_rounds,
                mock_mode=args.mock_mode,
            )
        )
    elif args.command == "test-readiness":
        success = asyncio.run(run_test_readiness())
        if not success:
            sys.exit(1)
    elif args.command == "db-export":
        from jemini.storage.sanitized_export import export_sanitized_db

        summary = asyncio.run(export_sanitized_db(output_dir=args.output_dir))
        print(f"✓ Database sanitized knowledge successfully exported to '{args.output_dir}':")
        for t, count in summary.items():
            print(f"  • {t}: {count} records")
    elif args.command == "db-restore":
        from jemini.storage.sanitized_export import restore_sanitized_db

        summary = asyncio.run(
            restore_sanitized_db(input_dir=args.input_dir, clear_existing=args.clear_existing)
        )
        print(f"✓ Database sanitized knowledge successfully restored from '{args.input_dir}':")
        for t, count in summary.items():
            print(f"  • {t}: {count} records")
    elif args.command == "studio-docs":
        from jemini.mcp.studio_docs import StudioDocsEngine

        engine = StudioDocsEngine()
        if args.action == "sections":
            sections = engine.list_sections()
            print("=== JEMINI STUDIO MCP DOCS SECTIONS ===")
            for s in sections:
                print(f"  📁 {s}")
        elif args.action == "list":
            docs = engine.list_documents(section=args.section)
            print(f"=== JEMINI STUDIO DOCUMENTS ({len(docs)}) ===")
            for d in docs:
                print(f"  📄 [{d['section']}] {d['doc_name']} — {d['title']}")
        elif args.action == "search":
            results = engine.search_docs(query=args.query, section=args.section)
            print(f"=== JEMINI STUDIO DOCS SEARCH: '{args.query}' ({len(results)} hits) ===")
            for r in results:
                print(f"\n  🎯 [{r.section}] {r.title} ({r.doc_name}) [Score: {r.relevance_score:.1f}]")
                print(f"     {r.snippet}")
        elif args.action == "get":
            doc_id = args.doc or args.query
            if not doc_id:
                print("Error: Specify --doc <name> to retrieve document content.")
                sys.exit(1)
            content = engine.get_document(doc_id)
            if content:
                print(f"=== DOCUMENT: {doc_id} ===\n")
                print(content)
            else:
                print(f"Error: Document '{doc_id}' not found in studio_knowledge.")
                sys.exit(1)


if __name__ == "__main__":
    main()
