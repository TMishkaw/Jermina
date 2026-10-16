"""Media Assets Hub & Free Resources Management.

Manages local offline audio/visual assets and procedural audio synthesis
(whoosh, hit, glitch, pop, chime) with zero external commercial dependencies.
"""

import logging
import math
import struct
import wave
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class MediaAssetType(str, Enum):
    SFX = "sfx"
    MUSIC = "music"
    GRAPHIC = "graphic"
    BROLL = "broll"


class MediaAssetItem(BaseModel):
    name: str
    asset_type: MediaAssetType
    local_path: str
    license_type: str = "CC0-PublicDomain"
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ProceduralSFXGenerator:
    """Synthesizes high-impact procedural sound effects (WAV 44.1kHz 16-bit mono)."""

    SAMPLE_RATE = 44100

    @classmethod
    def generate_whoosh(cls, output_path: Path, duration: float = 0.45) -> Path:
        """Fast dynamic whoosh transition with exponential pitch bend."""
        num_samples = int(duration * cls.SAMPLE_RATE)
        data = bytearray()
        for i in range(num_samples):
            t = i / num_samples
            freq = 150 + 600 * math.sin(math.pi * t)
            envelope = math.sin(math.pi * t) ** 2
            val = int(24000 * envelope * math.sin(2 * math.pi * freq * (i / cls.SAMPLE_RATE)))
            data.extend(struct.pack("<h", max(-32768, min(32767, val))))
        return cls._write_wav(output_path, bytes(data))

    @classmethod
    def generate_pop(cls, output_path: Path, duration: float = 0.15) -> Path:
        """Short punchy pop sound for UI bubbles or stickers."""
        num_samples = int(duration * cls.SAMPLE_RATE)
        data = bytearray()
        for i in range(num_samples):
            t = i / num_samples
            freq = 900 - 650 * t
            decay = math.exp(-18 * t)
            val = int(28000 * decay * math.sin(2 * math.pi * freq * (i / cls.SAMPLE_RATE)))
            data.extend(struct.pack("<h", max(-32768, min(32767, val))))
        return cls._write_wav(output_path, bytes(data))

    @classmethod
    def generate_hit(cls, output_path: Path, duration: float = 0.5) -> Path:
        """Heavy bass impact hit for hooks and title drops."""
        num_samples = int(duration * cls.SAMPLE_RATE)
        data = bytearray()
        for i in range(num_samples):
            t = i / num_samples
            freq = 120 - 70 * t
            decay = math.exp(-7 * t)
            val = int(31000 * decay * math.sin(2 * math.pi * freq * (i / cls.SAMPLE_RATE)))
            data.extend(struct.pack("<h", max(-32768, min(32767, val))))
        return cls._write_wav(output_path, bytes(data))

    @classmethod
    def generate_chime(cls, output_path: Path, duration: float = 0.6) -> Path:
        """Bright electronic chime for achievements, likes, or gifts."""
        num_samples = int(duration * cls.SAMPLE_RATE)
        data = bytearray()
        for i in range(num_samples):
            t = i / num_samples
            decay = math.exp(-5 * t)
            # Two harmonic frequencies: 523Hz (C5) + 659Hz (E5)
            val = int(14000 * decay * (
                math.sin(2 * math.pi * 523 * (i / cls.SAMPLE_RATE)) +
                math.sin(2 * math.pi * 659 * (i / cls.SAMPLE_RATE))
            ))
            data.extend(struct.pack("<h", max(-32768, min(32767, val))))
        return cls._write_wav(output_path, bytes(data))

    @classmethod
    def _write_wav(cls, output_path: Path, pcm_bytes: bytes) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(cls.SAMPLE_RATE)
            wf.writeframes(pcm_bytes)
        return output_path


class MediaAssetsHub:
    """Central registry and generator for all audio-visual media assets."""

    def __init__(self, assets_dir: Path | str | None = None):
        base = Path(assets_dir) if assets_dir else Path(__file__).resolve().parent.parent.parent.parent / "assets"
        self.assets_dir = base
        self.sfx_dir = base / "sfx"
        self.music_dir = base / "music"
        self.images_dir = base / "images"
        for d in (self.sfx_dir, self.music_dir, self.images_dir):
            d.mkdir(parents=True, exist_ok=True)

    def get_or_create_sfx(self, sfx_name: str) -> Path:
        """Returns existing SFX or generates procedural effect on the fly."""
        clean = sfx_name.lower().strip()
        wav_path = self.sfx_dir / f"{clean}.wav"
        if wav_path.exists():
            return wav_path

        if "whoosh" in clean:
            return ProceduralSFXGenerator.generate_whoosh(wav_path)
        elif "pop" in clean or "click" in clean:
            return ProceduralSFXGenerator.generate_pop(wav_path)
        elif "hit" in clean or "punch" in clean or "impact" in clean:
            return ProceduralSFXGenerator.generate_hit(wav_path)
        elif "chime" in clean or "bell" in clean or "like" in clean:
            return ProceduralSFXGenerator.generate_chime(wav_path)

        # Default fallback: pop
        return ProceduralSFXGenerator.generate_pop(wav_path)

    def list_all_assets(self) -> list[MediaAssetItem]:
        """Lists all registered assets across SFX, images, and audio."""
        items = []
        if self.assets_dir.exists():
            for p in self.assets_dir.rglob("*"):
                if p.is_file() and not p.name.startswith("."):
                    ext = p.suffix.lower()
                    if ext in [".wav", ".mp3", ".ogg"]:
                        asset_type = MediaAssetType.SFX if "sfx" in str(p) else MediaAssetType.MUSIC
                    elif ext in [".png", ".jpg", ".jpeg", ".svg"]:
                        asset_type = MediaAssetType.GRAPHIC
                    else:
                        continue

                    items.append(
                        MediaAssetItem(
                            name=p.stem,
                            asset_type=asset_type,
                            local_path=str(p),
                            license_type="CC0-PublicDomain",
                            tags=[p.parent.name, p.suffix.lstrip(".")],
                        )
                    )
        return items
