"""Remotion Video Renderer Service.

Renders programmatic 9:16 Shorts via local Remotion CLI or Docker container,
injecting synthesized audio, RMS-energy reactivity, and animated stickman cues.
"""

import asyncio
import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from jemini.orchestration.limits import PipelineLimits

logger = logging.getLogger(__name__)


class RenderOptions(BaseModel):
    composition_id: str = "StickmanShort9x16"
    aspect_ratio: str = "9:16"  # "9:16" for vertical Shorts, "16:9" for horizontal widescreen
    concurrency: int = Field(default=PipelineLimits.REMOTION.default_concurrency_workers)
    timeout_seconds: int = 360
    dry_run: bool = False

    @property
    def width(self) -> int:
        return 1920 if self.aspect_ratio in ["16:9", "widescreen", "horizontal"] else 1080

    @property
    def height(self) -> int:
        return 1080 if self.aspect_ratio in ["16:9", "widescreen", "horizontal"] else 1920



class RemotionRenderer:
    """Controls Remotion video compilation and rendering pipeline."""

    def __init__(self, remotion_dir: Path | str | None = None):
        base = (
            Path(remotion_dir)
            if remotion_dir
            else Path(__file__).resolve().parent.parent.parent.parent / "remotion"
        )
        self.remotion_dir = base
        self.public_dir = base / "public"
        self.out_dir = base / "out"
        self.public_dir.mkdir(parents=True, exist_ok=True)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def generate_stickman_cues(self, total_frames: int) -> list[dict[str, Any]]:
        """Generates dynamic acting cues tailored to video length with constant lively gesturing."""
        cues: list[dict[str, Any]] = []
        current_frame = 0

        # Sequence palette: (animation, eyeType, mouthType, prop)
        motion_sequence = [
            ("surprised", "wide", "gasp", "none"),
            ("talk", "neutral", "talking", "microphone"),
            ("point_up", "wink", "smile", "none"),
            ("laugh", "happy", "smile", "coffee"),
            ("talk", "happy", "talking", "none"),
            ("point_up", "neutral", "talking", "none"),
            ("celebrate", "happy", "smile", "none"),
        ]

        step_duration = 75  # ~2.5 seconds per cue at 30fps
        idx = 0
        while current_frame < total_frames:
            dur = min(step_duration, total_frames - current_frame)
            anim, eye, mouth, prop = motion_sequence[idx % len(motion_sequence)]
            cues.append({
                "fromFrame": current_frame,
                "durationInFrames": dur,
                "animation": anim,
                "eyeType": eye,
                "mouthType": mouth,
                "prop": prop,
            })
            current_frame += dur
            idx += 1

        return cues

    async def render_video(
        self,
        title: str,
        hook_text: str,
        audio_path: Path | str,
        audio_rms: list[float],
        subtitles: list[dict[str, Any]],
        output_mp4: Path | str,
        accent_color: str = "#00F0FF",
        aspect_ratio: str = "9:16",
        options: RenderOptions | None = None,
    ) -> Path:
        """Renders video (9:16 Shorts or 16:9 Widescreen) with synced audio, subtitles, and stickman rig."""
        opts = options or RenderOptions()
        if aspect_ratio in ("16:9", "widescreen", "horizontal") or opts.aspect_ratio in ("16:9", "widescreen", "horizontal"):
            opts.composition_id = "CyberStudio16x9"
            opts.aspect_ratio = "16:9"
        else:
            opts.composition_id = "StickmanShort9x16"
            opts.aspect_ratio = "9:16"

        out_file = Path(output_mp4).resolve()
        out_file.parent.mkdir(parents=True, exist_ok=True)

        audio_src = Path(audio_path).resolve()
        public_audio = self.public_dir / "voice_track.wav"

        # Copy audio track to Remotion public folder
        if audio_src.exists() and audio_src != public_audio:
            shutil.copyfile(audio_src, public_audio)

        total_frames = len(audio_rms) if audio_rms else 360
        stickman_cues = self.generate_stickman_cues(total_frames)

        # Build props payload
        config_payload = {
            "id": out_file.stem,
            "title": title,
            "hookText": hook_text,
            "accentColor": accent_color,
            "audioSrc": "voice_track.wav",
            "totalFrames": total_frames,
            "audioRms": audio_rms,
            "stickmanCues": stickman_cues,
            "subtitles": subtitles,
        }

        props_file = self.remotion_dir / "active_props.json"
        props_file.write_text(json.dumps({"config": config_payload}, indent=2, ensure_ascii=False), encoding="utf-8")

        if opts.dry_run:
            logger.info("Executing Remotion dry-run render for %s...", out_file.name)
            out_file.write_bytes(b"MOCK_MP4_CONTAINER_PAYLOAD")
            return out_file

        logger.info(
            "Starting Remotion render (%d frames, concurrency: %d) -> %s",
            total_frames,
            opts.concurrency,
            out_file.name,
        )

        # Execute Remotion render using shell
        cmd_str = (
            f'npx remotion render src/index.ts {opts.composition_id} '
            f'"{out_file}" --props="{props_file}" --concurrency={opts.concurrency}'
        )

        proc = await asyncio.create_subprocess_shell(
            cmd_str,
            cwd=str(self.remotion_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=opts.timeout_seconds)
        except asyncio.TimeoutError as exc:
            proc.kill()
            msg = f"Remotion render exceeded timeout of {opts.timeout_seconds}s"
            raise TimeoutError(msg) from exc

        if proc.returncode != 0:
            error_output = stderr.decode("utf-8", errors="replace") or stdout.decode("utf-8", errors="replace")
            logger.error("Remotion render failed with exit code %d:\n%s", proc.returncode, error_output)
            msg = f"Remotion render failed (code {proc.returncode}): {error_output[:400]}"
            raise RuntimeError(msg)

        logger.info("Successfully rendered video: %s (%.2f MB)", out_file.name, out_file.stat().st_size / (1024 * 1024))
        return out_file

    # Alias for backward compatibility
    render_short = render_video

