"""Unit tests for Trend Scout and Production Queue."""

import pytest

from jemini.core.context import ChannelRegistry
from jemini.scheduling.models import QueueTaskStatus
from jemini.scheduling.queue import ProductionQueue
from jemini.scheduling.scout import TrendScout


@pytest.mark.asyncio
async def test_trend_scout_mock():
    scout = TrendScout()
    profile = ChannelRegistry.get("cyber_matrix")
    scouted = await scout.scout_topics(profile=profile, count=2, mock_mode=True)

    assert len(scouted.topics) == 2
    assert "zero-day" in scouted.topics[0].title.lower() or "linux" in scouted.topics[0].title.lower()
    assert scouted.topics[0].relevance_score >= 8.0
    assert len(scouted.topics[0].keywords) > 0


def test_production_queue_lifecycle(tmp_path):
    queue_file = tmp_path / "test_queue.json"
    queue = ProductionQueue(queue_file=queue_file)

    # 1. Enqueue
    task1 = queue.enqueue(channel_id="stickman_lab", topic="Test AI topic 1")
    task2 = queue.enqueue(channel_id="cyber_matrix", topic="Test Cyber topic 2")
    assert task1.status == QueueTaskStatus.QUEUED
    assert task2.status == QueueTaskStatus.QUEUED

    # 2. Dequeue pending (FIFO)
    next_task = queue.get_next_pending()
    assert next_task is not None
    assert next_task.task_id == task1.task_id
    assert next_task.status == QueueTaskStatus.PROCESSING

    # 3. Complete task
    completed = queue.complete_task(
        task_id=task1.task_id,
        video_path="output/test_video.mp4",
        validation_score=9.5,
    )
    assert completed is not None
    assert completed.status == QueueTaskStatus.COMPLETED
    assert completed.completed_at is not None

    # 4. Fail next task
    next_task2 = queue.get_next_pending()
    assert next_task2 is not None
    assert next_task2.task_id == task2.task_id

    failed = queue.fail_task(task_id=task2.task_id, error_message="Simulated render crash")
    assert failed is not None
    assert failed.status == QueueTaskStatus.FAILED

    # 5. Persistence across new instance
    new_queue = ProductionQueue(queue_file=queue_file)
    tasks = new_queue.list_tasks()
    assert len(tasks) == 2
    assert any(t.status == QueueTaskStatus.COMPLETED for t in tasks)
    assert any(t.status == QueueTaskStatus.FAILED for t in tasks)
