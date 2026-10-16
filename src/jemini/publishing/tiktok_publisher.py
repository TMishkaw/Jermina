"""TikTok Automated Publishing Engine via Playwright Persistent Profile.

Automates video publishing to TikTok Studio using saved browser session state,
supports multi-channel tag formatting, headless execution, and database audit logging.
"""

from __future__ import annotations

import asyncio
import datetime
import json
import logging
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field
from sqlalchemy import text

from jemini.core.context import ChannelRegistry
from jemini.storage.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class TikTokPrivacyStatus(str, Enum):
    PUBLIC = "public"
    FRIENDS = "friends"
    PRIVATE = "private"


class TikTokMetadata(BaseModel):
    """Specification of TikTok video upload metadata."""

    title: str
    description: str = ""
    tags: list[str] = Field(default_factory=lambda: ["#Shorts", "#AI", "#Jemini"])
    privacy_status: TikTokPrivacyStatus = TikTokPrivacyStatus.PUBLIC
    allow_comments: bool = True
    allow_duet: bool = True
    allow_stitch: bool = True


class PublishedTikTokResult(BaseModel):
    """Result returned after TikTok publishing."""

    success: bool
    video_path: str
    caption: str
    status: str
    uploaded_at: str
    error: str | None = None
    screenshot_path: str | None = None


class TikTokPublisher:
    """Manages TikTok Studio video upload via Playwright."""

    def __init__(
        self,
        session_path: Path | str | None = None,
        user_data_dir: Path | str | None = None,
    ):
        base = Path(__file__).resolve().parent.parent.parent.parent
        config_dir = base / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        self.session_file = (
            Path(session_path) if session_path else self._discover_session_file(config_dir)
        )
        self.user_data_dir = (
            Path(user_data_dir) if user_data_dir else self._discover_user_data_dir(config_dir)
        )

    def _discover_session_file(self, config_dir: Path) -> Path:
        candidates = [
            config_dir / "tiktok_session.json",
            Path("D:/JERMINA/config/tiktok_session.json"),
            Path("D:/ai-video/tiktok_session.json"),
        ]
        for c in candidates:
            if c.exists():
                return c
        return config_dir / "tiktok_session.json"

    def _discover_user_data_dir(self, config_dir: Path) -> Path:
        candidates = [
            config_dir / "tiktok_browser_profile",
            Path("D:/JERMINA/config/tiktok_browser_profile"),
            Path("D:/ai-video/tiktok_browser_profile"),
        ]
        for c in candidates:
            if c.exists():
                return c
        return config_dir / "tiktok_browser_profile"

    def has_credentials(self) -> bool:
        """Returns True if a persistent browser profile or session file exists."""
        return self.session_file.exists() or self.user_data_dir.exists()

    def format_caption(
        self,
        title: str,
        channel_id: str = "stickman_lab",
        extra_tags: list[str] | None = None,
    ) -> str:
        """Formats caption with channel-specific tags and branding."""
        clean_title = title.replace("#Shorts", "").replace("#shorts", "").strip()

        profile = ChannelRegistry.get(channel_id)
        channel_tags = profile.default_tags if profile else ["#AI", "#Tech"]

        combined_tags: list[str] = []
        for t in channel_tags + (extra_tags or []):
            tag = t if t.startswith("#") else f"#{t}"
            if tag not in combined_tags:
                combined_tags.append(tag)

        # Brand tag
        if "#Jemini" not in combined_tags and "#jemini" not in combined_tags:
            combined_tags.append("#Jemini")

        tags_str = " ".join(combined_tags)
        return f"{clean_title}\n\n{tags_str}".strip()

    async def publish_video(
        self,
        video_path: Path | str,
        metadata: TikTokMetadata,
        channel_id: str = "stickman_lab",
        headless: bool = True,
        mock_mode: bool = False,
    ) -> PublishedTikTokResult:
        """Uploads video to TikTok via Playwright session."""
        v_path = Path(video_path)
        if not v_path.exists() and not mock_mode:
            msg = f"Video file not found at: {v_path}"
            logger.error(msg)
            return PublishedTikTokResult(
                success=False,
                video_path=str(v_path),
                caption=metadata.title,
                status="FAILED",
                uploaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                error=msg,
            )

        caption = self.format_caption(
            title=metadata.title,
            channel_id=channel_id,
            extra_tags=metadata.tags,
        )

        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if mock_mode:
            logger.info("[MOCK] Simulating TikTok upload for %s", v_path.name)
            res = PublishedTikTokResult(
                success=True,
                video_path=str(v_path),
                caption=caption,
                status="PUBLISHED_MOCK",
                uploaded_at=now_str,
            )
            await self._record_audit_log(channel_id, res)
            return res

        if not self.has_credentials():
            msg = f"TikTok session/profile not found in {self.session_file} or {self.user_data_dir}"
            logger.error(msg)
            return PublishedTikTokResult(
                success=False,
                video_path=str(v_path),
                caption=caption,
                status="FAILED",
                uploaded_at=now_str,
                error=msg,
            )

        # Run Playwright in an asyncio-compatible thread
        return await asyncio.to_thread(
            self._sync_playwright_upload,
            v_path=v_path,
            caption=caption,
            channel_id=channel_id,
            headless=headless,
        )

    def _sync_playwright_upload(
        self,
        v_path: Path,
        caption: str,
        channel_id: str,
        headless: bool,
    ) -> PublishedTikTokResult:
        """Synchronous implementation of Playwright automation."""
        import time

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as err:
            msg = f"Playwright is not installed: {err}"
            logger.error(msg)
            return PublishedTikTokResult(
                success=False,
                video_path=str(v_path),
                caption=caption,
                status="FAILED",
                uploaded_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                error=msg,
            )

        screenshot_path = str(v_path.parent / f"tiktok_upload_{int(time.time())}.png")
        now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        logger.info("[TIKTOK] Starting TikTok Studio upload for: %s", v_path.name)
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(self.user_data_dir),
                headless=headless,
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )

            page = browser.pages[0] if browser.pages else browser.new_page()
            page.set_default_timeout(60000)

            try:
                page.goto("https://www.tiktok.com/tiktokstudio/upload", wait_until="domcontentloaded")
                time.sleep(4)

                # Check if redirected to login
                if "login" in page.url.lower():
                    browser.close()
                    msg = "TikTok session has expired. Re-authentication required."
                    logger.error(msg)
                    return PublishedTikTokResult(
                        success=False,
                        video_path=str(v_path),
                        caption=caption,
                        status="EXPIRED_SESSION",
                        uploaded_at=now_str,
                        error=msg,
                    )

                # Dismiss cancel popup if exists
                cancel_btn = page.locator('button:has-text("Cancel")')
                if cancel_btn.count() > 0 and cancel_btn.first.is_visible():
                    cancel_btn.first.click(force=True)
                    time.sleep(1)

                # Find file input
                input_file = page.locator('input[type="file"]')
                if input_file.count() == 0:
                    page.screenshot(path=screenshot_path)
                    browser.close()
                    msg = f"File input not found on TikTok Studio page. Screenshot: {screenshot_path}"
                    return PublishedTikTokResult(
                        success=False,
                        video_path=str(v_path),
                        caption=caption,
                        status="ELEMENT_NOT_FOUND",
                        uploaded_at=now_str,
                        error=msg,
                        screenshot_path=screenshot_path,
                    )

                logger.info("[TIKTOK] Submitting video file: %s", v_path.resolve())
                input_file.first.set_input_files(str(v_path.resolve()))

                # Wait for video upload to process
                time.sleep(10)

                # Type caption
                editor = page.locator('div[contenteditable="true"]').first
                if editor.count() > 0:
                    editor.click(force=True)
                    page.keyboard.press("Control+A")
                    page.keyboard.press("Backspace")
                    page.keyboard.type(caption, delay=15)
                    time.sleep(2)
                    logger.info("[TIKTOK] Caption entered successfully.")

                # Scroll down
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(2)

                # Find Post button
                post_btn = page.locator('button:has-text("Post"), button:has-text("Опублікувати")').last
                if post_btn.count() == 0:
                    page.screenshot(path=screenshot_path)
                    browser.close()
                    msg = f"Post button not found. Screenshot: {screenshot_path}"
                    return PublishedTikTokResult(
                        success=False,
                        video_path=str(v_path),
                        caption=caption,
                        status="POST_BUTTON_NOT_FOUND",
                        uploaded_at=now_str,
                        error=msg,
                        screenshot_path=screenshot_path,
                    )

                post_btn.scroll_into_view_if_needed()
                time.sleep(1)
                post_btn.click(force=True)
                time.sleep(5)

                page.screenshot(path=screenshot_path)
                browser.close()

                logger.info("✓ [TIKTOK] Successfully posted video to TikTok Studio!")
                return PublishedTikTokResult(
                    success=True,
                    video_path=str(v_path),
                    caption=caption,
                    status="PUBLISHED",
                    uploaded_at=now_str,
                    screenshot_path=screenshot_path,
                )

            except Exception as err:  # noqa: BLE001
                page.screenshot(path=screenshot_path)
                browser.close()
                msg = f"Playwright upload failed: {err}"
                logger.error(msg)
                return PublishedTikTokResult(
                    success=False,
                    video_path=str(v_path),
                    caption=caption,
                    status="ERROR",
                    uploaded_at=now_str,
                    error=msg,
                    screenshot_path=screenshot_path,
                )

    async def _record_audit_log(self, channel_id: str, res: PublishedTikTokResult) -> None:
        """Stores TikTok publishing log in PostgreSQL."""
        try:
            async with AsyncSessionLocal() as session:
                query = text("""
                    INSERT INTO channel_audit_logs (channel_id, action, status, details, created_at)
                    VALUES (:cid, :action, :status, :details, NOW())
                """)
                payload = {
                    "cid": channel_id,
                    "action": "publish_tiktok",
                    "status": "success" if res.success else "failed",
                    "details": json.dumps({
                        "platform": "tiktok",
                        "status": res.status,
                        "caption": res.caption[:100],
                        "video_path": res.video_path,
                    }),
                }
                await session.execute(query, payload)
                await session.commit()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to record TikTok audit log in DB: %s", exc)

