import shutil
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class JeminiSettings(BaseSettings):
    """Central configuration for Jemini core engine."""
    
    # Environment mode: dev, test, release
    environment: str = Field(default="dev", alias="JEMINI_ENV")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/jemini",
        alias="DATABASE_URL"
    )
    
    # Gemini API keys pool
    gemini_api_keys: list[str] = Field(default_factory=list, alias="GEMINI_API_KEYS")
    gemini_primary_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_PRIMARY_MODEL")
    gemini_live_model: str = Field(default="gemini-3.8-live", alias="GEMINI_LIVE_MODEL")
    
    # Media tools
    ffmpeg_path: str = Field(default="ffmpeg", alias="FFMPEG_PATH")

    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def resolve_ffmpeg_path(self) -> str:
        """Resolves the executable path for ffmpeg."""
        if self.ffmpeg_path and self.ffmpeg_path != "ffmpeg" and Path(self.ffmpeg_path).exists():
            return str(Path(self.ffmpeg_path).resolve())
        which_path = shutil.which("ffmpeg")

        if which_path:
            return which_path
        candidates = [
            Path("D:/Clipping/bin/ffmpeg.exe"),
            Path("C:/Clipping/bin/ffmpeg.exe"),
            Path("C:/ffmpeg/bin/ffmpeg.exe"),
            Path("D:/ffmpeg/bin/ffmpeg.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())
        return "ffmpeg"


settings = JeminiSettings()

