"""Persistent Production Queue for Autonomous Video Generation."""

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jemini.scheduling.models import ProductionTask, QueueTaskStatus

logger = logging.getLogger(__name__)


class ProductionQueue:
    """Manages queued generation tasks with file-backed persistence."""

    def __init__(self, queue_file: Path | str = "output/production_queue.json"):
        self.queue_file = Path(queue_file).resolve()
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self._tasks: dict[str, ProductionTask] = {}
        self._load()

    def _load(self) -> None:
        if self.queue_file.exists():
            try:
                raw = self.queue_file.read_text(encoding="utf-8")
                data = json.loads(raw)
                for item in data:
                    task = ProductionTask.model_validate(item)
                    self._tasks[task.task_id] = task
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to load queue file %s: %s", self.queue_file, exc)

    def _save(self) -> None:
        try:
            items = [t.model_dump(mode="json") for t in self._tasks.values()]
            self.queue_file.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to persist queue to %s: %s", self.queue_file, exc)

    def enqueue(self, channel_id: str, topic: str, metadata: dict[str, Any] | None = None) -> ProductionTask:
        """Adds a new topic to the generation queue."""
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task = ProductionTask(
            task_id=task_id,
            channel_id=channel_id,
            topic=topic,
            status=QueueTaskStatus.QUEUED,
            metadata=metadata or {},
        )
        self._tasks[task_id] = task
        self._save()
        logger.info("Enqueued task %s for channel '%s': '%s'", task_id, channel_id, topic)
        return task

    def get_next_pending(self, channel_id: str | None = None) -> ProductionTask | None:
        """Retrieves and locks the oldest QUEUED task, transitioning to PROCESSING."""
        queued = [
            t for t in self._tasks.values()
            if t.status == QueueTaskStatus.QUEUED and (channel_id is None or t.channel_id == channel_id)
        ]
        if not queued:
            return None
        # Sort by created_at ascending
        queued.sort(key=lambda t: t.created_at)
        target = queued[0]
        target.status = QueueTaskStatus.PROCESSING
        self._save()
        return target

    def complete_task(
        self,
        task_id: str,
        video_path: str,
        validation_score: float | None = None,
    ) -> ProductionTask | None:
        """Marks a task as successfully COMPLETED."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = QueueTaskStatus.COMPLETED
        task.video_path = video_path
        task.validation_score = validation_score
        task.completed_at = datetime.now(timezone.utc)
        self._save()
        logger.info("Task %s completed successfully (score: %s)", task_id, validation_score)
        return task

    def fail_task(self, task_id: str, error_message: str) -> ProductionTask | None:
        """Marks a task as FAILED with error explanation."""
        task = self._tasks.get(task_id)
        if not task:
            return None
        task.status = QueueTaskStatus.FAILED
        task.error_message = error_message
        task.completed_at = datetime.now(timezone.utc)
        self._save()
        logger.warning("Task %s failed: %s", task_id, error_message)
        return task

    def list_tasks(self, status: QueueTaskStatus | None = None) -> list[ProductionTask]:
        """Lists tasks filtered optionally by status."""
        tasks = list(self._tasks.values())
        if status:
            tasks = [t for t in tasks if t.status == status]
        tasks.sort(key=lambda t: t.created_at)
        return tasks
