from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class JeminiSettings(BaseSettings):
    """Central configuration for Jemini core engine."""
    
    # Environment mode: dev, test, release
    environment: str = Field(default="dev", alias="JEMINI_ENV")
    
    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/jemini",
        alias="DATABASE_URL"
    )
    
    # Gemini API keys pool
    gemini_api_keys: List[str] = Field(default_factory=list, alias="GEMINI_API_KEYS")
    gemini_primary_model: str = Field(default="gemini-2.5-flash", alias="GEMINI_PRIMARY_MODEL")
    gemini_live_model: str = Field(default="gemini-3.8-live", alias="GEMINI_LIVE_MODEL")
    
    # API Server
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = JeminiSettings()
