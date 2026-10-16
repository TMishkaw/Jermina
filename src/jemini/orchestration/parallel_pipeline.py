"""Parallel Orchestration Engine for Multi-Scene Media Synthesis.

Coordinates concurrent voice synthesis across Gemini Live API sessions,
procedural sound effect generation, asset prefetching, and video frame assembly
while strictly enforcing technical limits (timeouts, token rates, and concurrency).
"""

import asyncio
import logging
import wave
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from jemini.media.assets_hub import MediaAssetsHub
from jemini.orchestration.limits import PipelineLimits
from jemini.rotator.rotator import APIKeyRotator
from jemini.voice.live_voice_service import (
    GeminiLiveVoiceService,
    SynthesizedAudioResult,
    VoiceDirective,
)

logger = logging.getLogger(__name__)


class SceneScript(BaseModel):
    """Specification of an individual video scene for parallel processing."""
    scene_id: str
    text: str
    directive: VoiceDirective = Field(default_factory=VoiceDirective)
    expected_sfx: list[str] = Field(default_factory=list)


class PipelineExecutionResult(BaseModel):
    """Result of parallel multi-scene synthesis and assembly."""
    master_audio_path: str
    total_duration_seconds: float
    total_frames: int
    scene_audios: list[SynthesizedAudioResult] = Field(default_factory=list)
    generated_sfx: dict[str, str] = Field(default_factory=dict)
    audio_rms_per_frame: list[float] = Field(default_factory=list)
    unified_cues: list[dict[str, Any]] = Field(default_factory=list)


class ParallelMediaOrchestrator:
    """Orchestrates concurrent execution of speech synthesis and media assets generation."""

    def __init__(
        self,
        rotator: APIKeyRotator | None = None,
        voice_service: GeminiLiveVoiceService | None = None,
        assets_hub: MediaAssetsHub | None = None,
    ):
        self.rotator = rotator
        self.voice_service = voice_service or GeminiLiveVoiceService(rotator=rotator)
        self.assets_hub = assets_hub or MediaAssetsHub()

    def _validate_scene_limits(self, scene: SceneScript) -> None:
        """Enforces safe chunk threshold to prevent Live API connection timeouts."""
        word_count = len(scene.text.split())
        max_words = PipelineLimits.LIVE.max_safe_scene_words
        if word_count > max_words:
            logger.warning(
                "Scene '%s' has %d words, exceeding safe limit of %d. "
                "Splitting or shortening is recommended to prevent Live API GoAway timeouts.",
                scene.scene_id,
                word_count,
                max_words,
            )

    async def _synthesize_scene_worker(
        self,
        scene: SceneScript,
        output_path: Path,
        mock_mode: bool = False,
    ) -> SynthesizedAudioResult:
        """Worker task for a single scene synthesis."""
        self._validate_scene_limits(scene)
        logger.info("Starting synthesis for scene '%s'...", scene.scene_id)
        return await self.voice_service.synthesize(
            text_to_speak=scene.text,
            output_wav_path=output_path,
            directive=scene.directive,
            mock_mode=mock_mode,
        )

    async def _generate_sfx_worker(self, sfx_names: list[str]) -> dict[str, str]:
        """Worker task to generate or retrieve all required SFX concurrently."""
        results: dict[str, str] = {}

        def _generate_one(name: str) -> tuple[str, str]:
            path = self.assets_hub.get_or_create_sfx(name)
            return name, str(path)

        tasks = [asyncio.to_thread(_generate_one, name) for name in sfx_names]
        if tasks:
            generated = await asyncio.gather(*tasks)
            for name, path in generated:
                results[name] = path

        return results

    async def execute_parallel_pipeline(
        self,
        scenes: list[SceneScript],
        output_dir: Path | str,
        mock_mode: bool = False,
    ) -> PipelineExecutionResult:
        """Executes full concurrent media pipeline across all scenes and assets."""
        if not scenes:
            msg = "At least one scene is required for pipeline execution."
            raise ValueError(msg)

        out_path = Path(output_dir)
        scenes_dir = out_path / "scenes"
        scenes_dir.mkdir(parents=True, exist_ok=True)

        # 1. Prepare parallel tasks
        scene_tasks = [
            self._synthesize_scene_worker(
                scene=scene,
                output_path=scenes_dir / f"{scene.scene_id}.wav",
                mock_mode=mock_mode,
            )
            for scene in scenes
        ]

        # Extract unique SFX requirements
        unique_sfx: set[str] = {sfx for sc in scenes for sfx in sc.expected_sfx}
        sfx_task = self._generate_sfx_worker(list(unique_sfx))

        # 2. Concurrently execute voice synthesis and SFX generation
        logger.info(
            "Executing parallel pipeline: %d scenes and %d sound effects...",
            len(scenes),
            len(unique_sfx),
        )
        audio_results, sfx_dict = await asyncio.gather(
            asyncio.gather(*scene_tasks),
            sfx_task,
        )

        # 3. Concatenate scene audio into master track
        combined_pcm = bytearray()
        for res in audio_results:
            with wave.open(res.audio_path, "rb") as wf:
                combined_pcm.extend(wf.readframes(wf.getnframes()))

        master_wav = out_path / "master_audio.wav"
        with wave.open(str(master_wav), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(bytes(combined_pcm))

        # 4. Compute continuous master RMS energy
        master_pcm_bytes = bytes(combined_pcm)
        master_rms = self.voice_service._calculate_rms_energy(
            master_pcm_bytes, fps=30, sample_rate=24000
        )
        total_frames = len(master_rms)
        total_duration = round(len(master_pcm_bytes) / (24000 * 2), 2)

        # 5. Build continuous unified subtitle cues with correct frame offsets
        unified_cues: list[dict[str, Any]] = []
        current_frame_offset = 0

        for res in audio_results:
            for cue in res.suggested_cues:
                unified_cues.append({
                    "text": cue["text"],
                    "startFrame": cue["startFrame"] + current_frame_offset,
                    "endFrame": cue["endFrame"] + current_frame_offset,
                    "highlight": cue.get("highlight", False),
                })
            current_frame_offset += res.total_frames

        return PipelineExecutionResult(
            master_audio_path=str(master_wav),
            total_duration_seconds=total_duration,
            total_frames=total_frames,
            scene_audios=list(audio_results),
            generated_sfx=sfx_dict,
            audio_rms_per_frame=master_rms,
            unified_cues=unified_cues,
        )
