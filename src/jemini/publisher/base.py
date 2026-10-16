"""Base publisher interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class PublicationPayload(BaseModel):
    video_path: str
    title: str
    description: str
    tags: list[str] = []
    is_short: bool = False
    privacy_status: str = "public"  # public, private, unlisted

class PublicationResult(BaseModel):
    success: bool
    platform: str
    remote_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None

class BasePublisher(ABC):
    @abstractmethod
    async def publish(self, payload: PublicationPayload) -> PublicationResult:
        pass
