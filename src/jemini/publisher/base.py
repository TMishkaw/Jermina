"""Base publisher interface."""

from abc import ABC, abstractmethod

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
    remote_id: str | None = None
    url: str | None = None
    error: str | None = None

class BasePublisher(ABC):
    @abstractmethod
    async def publish(self, payload: PublicationPayload) -> PublicationResult:
        pass
