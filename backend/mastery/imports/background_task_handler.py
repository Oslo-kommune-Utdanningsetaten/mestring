import os
import time
import uuid
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from mastery.models import DataMaintenanceTask

WORKER_ID = f"worker-{uuid.uuid4()}"
HEARTBEAT_EVERY = 5          # seconds
LOCK_TIMEOUT = timedelta(minutes=10)
RETRY_BACKOFF = [30, 120, 600]  # seconds


def claim_next_task():
    now = timezone.now()
    stale = now - LOCK_TIMEOUT
    with transaction.atomic():
        task = (
            DataMaintenanceTask.objects
            .select_for_update(skip_locked=True)
            .filter(
                Q(status="pending") |
                Q(status="running", locked_at__lt=stale)  # requeue stale
            )
            .order_by("created_at")
            .first()
        )
        if not task:
            return None
        task.status = "running"
        task.locked_at = now
        task.locked_by = WORKER_ID
        task.last_heartbeat_at = now
        task.save(update_fields=["status", "locked_at", "locked_by", "last_heartbeat_at"])
        return task


def heartbeat(task):
    task.last_heartbeat_at = timezone.now()
    DataMaintenanceTask.objects.filter(id=task.id).update(last_heartbeat_at=task.last_heartbeat_at)


def run():
    while True:
        task = claim_next_task()
        if not task:
            time.sleep(1)
            continue
        try:
            # do work in chunks, update progress + heartbeat
            for chunk in do_work(task):
                task.results = chunk.progress  # keep small; consider separate log table
                heartbeat(task)
                time.sleep(HEARTBEAT_EVERY)
            task.status = "completed"
            task.completed_at = timezone.now()
            task.error = None
            task.attempts = (task.attempts or 0)
        except Exception as e:
            attempts = (task.attempts or 0) + 1
            task.attempts = attempts
            task.error = str(e)[:1000]
            if attempts >= len(RETRY_BACKOFF) + 1:
                task.status = "failed"
            else:
                task.status = "pending"
                task.run_at = timezone.now() + timedelta(seconds=RETRY_BACKOFF[attempts - 1])
        finally:
            # release lock
            task.locked_at = None
            task.locked_by = None
            task.save()
