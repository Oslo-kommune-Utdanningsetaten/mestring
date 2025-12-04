from mastery.data_import.feide_api import fetch_groups_from_feide, fetch_memberships_from_feide
import names
import time
import logging
import threading
import traceback
from datetime import timedelta
import json
from django.db import transaction
from django.utils import timezone
from mastery.models import DataMaintenanceTask, generate_nanoid
from .import_school import school_update
from .import_groups import import_groups_from_file
from .import_users import import_memberships_from_file
from .cleaner_bot import update_data_integrity

logger = logging.getLogger(__name__)

# Retries after initial attempt. Retry in 1, 3, 10 minutes before giving up.
RETRY_BACKOFF = [1*60, 3*60, 10*60]
HANDLER_NAME = f"{names.get_first_name()} {generate_nanoid(size=6)}"


# Find next pending task, set status to running and return it
def claim_next_task():
    now = timezone.now()
    with transaction.atomic():
        task = (
            DataMaintenanceTask.objects
            .select_for_update(skip_locked=True)
            .filter(status="pending", handler_name=None, earliest_run_at__lte=now)
            .order_by("created_at")
            .first()
        )
        if not task:
            return None
        task.status = "running"
        task.started_at = now
        task.last_heartbeat_at = now
        task.handler_name = HANDLER_NAME
        task.attempts = task.attempts + 1
        task.save(update_fields=["status", "started_at", "handler_name",
                  "last_heartbeat_at", "attempts", "updated_at"])
        return task


# For each chunk of work done, update the progress
def update_progress(task, result):
    # Merge incoming result without overwriting existing errors.
    with transaction.atomic():
        # Use select_for_update to avoid race conditions (not currently necessary, but future-proof)
        persisted = DataMaintenanceTask.objects.select_for_update().only("id", "result").get(id=task.id)
        persisted_result = persisted.result or {}
        incoming = result or {}
        merged = dict(persisted_result)

        # Merge/append errors
        persisted_errors = merged.get("errors", []) or []
        incoming_errors = incoming.get("errors", []) or []
        # Avoid duplicating identical error entries by deterministic JSON serialization
        try:
            seen = {json.dumps(e, sort_keys=True) for e in persisted_errors}
        except Exception:
            seen = set()
        for error in incoming_errors:
            try:
                s = json.dumps(error, sort_keys=True)
            except Exception:
                # Fallback, just in case
                s = str(error)
            if s not in seen:
                persisted_errors.append(error)
                seen.add(s)

        merged.update(incoming)
        merged["errors"] = persisted_errors
        # Update the task result and last_heartbeat_at
        DataMaintenanceTask.objects.filter(id=task.id).update(result=merged, last_heartbeat_at=timezone.now())


def next_execution_time(task):
    delay = RETRY_BACKOFF[task.attempts - 1]
    return timezone.now() + timedelta(seconds=delay)


def append_error_to_result(task, error_as_string):
    result = task.result or {}
    errors = result.get("errors", [])
    errors.append({"error": "unexpected-error", "message": error_as_string})
    result["errors"] = errors
    return result


def do_work(task):
    '''
    The yield from do_work(task) MUST produce dicts on this format:
    {
        "result": {
            "entity": "school",
            "action": "update",
            "errors": [{error: "...", message: "..."}],
            "changes": {} # optional, depending on action
            "counts": {} # optional, depending on action
        },
        "is_done": True|False,
    }
    '''
    job_params = task.job_params or {}
    org_number = job_params.get("org_number")
    if not org_number:
        raise ValueError(f"Missing org_number for job_name '{task.job_name}'")

    if task.job_name == "update_schools":
        yield from school_update(org_number)
    elif task.job_name == "fetch_groups_from_feide":
        yield from fetch_groups_from_feide(org_number)
    elif task.job_name == "fetch_memberships_from_feide":
        yield from fetch_memberships_from_feide(org_number)
    elif task.job_name == "import_groups":
        yield from import_groups_from_file(org_number)
    elif task.job_name == "import_memberships":
        yield from import_memberships_from_file(org_number)
    elif task.job_name == "update_data_integrity":
        print("Running update_data_integrity", task.id, task.job_params.get("maintained_earlier_than"))
        yield from update_data_integrity(org_number, task.job_params.get("maintained_earlier_than"))
    else:
        raise ValueError(f"Unknown job_name '{task.job_name}'")


# Used on manual one-off tasks, or in tests
def run():
    task = claim_next_task()
    if task:
        try:
            # do work in chunks, update progress in result
            for chunk in do_work(task):
                update_progress(task, chunk.get("result"))
                if chunk.get("is_done"):
                    break
            task.status = "finished"
            task.finished_at = timezone.now()
            task.save(update_fields=["status", "finished_at", "updated_at"])
        except Exception as error:
            logger.error(f"Task {task.job_name} (id: {task.id}) failed: {error}", exc_info=True)
            tb = traceback.format_exc()
            error_as_string = str(error) + f". {tb}"
            with transaction.atomic():
                # refresh task to avoid stale data
                task = (DataMaintenanceTask.objects.select_for_update().only(
                    "id", "result", "attempts", "status", "handler_name", "earliest_run_at", "updated_at",
                    "failed_at").get(id=task.id))
                # append error to result
                task.result = append_error_to_result(task, error_as_string)

                if task.attempts <= len(RETRY_BACKOFF):
                    # failed, but schedule retry
                    task.status = "pending"
                    task.handler_name = None
                    task.failed_at = None
                    task.earliest_run_at = next_execution_time(task)
                else:
                    # failed, no more retries
                    logger.error(
                        f"Task {task.job_name} (id: {task.id}) permanently failed after {task.attempts} attempts")
                    task.status = "failed"
                    task.failed_at = timezone.now()
                    task.earliest_run_at = None

                task.save(update_fields=[
                    "result", "attempts", "status", "handler_name",
                    "earliest_run_at", "failed_at", "updated_at"
                ])
        logger.info(f"Task {task.job_name} (id: {task.id}) completed with status '{task.status}'")
        return task
    return None


class BackgroundTaskRunner:
    def __init__(self, sleep_seconds: int = 2):
        self.sleep_seconds = sleep_seconds
        self._shutdown_event = threading.Event()

    def shutdown(self):
        self._shutdown_event.set()

    def run_once(self):
        return run()

    def run_forever(self):
        while not self._shutdown_event.is_set():
            self.run_once()
            if self._shutdown_event.wait(timeout=self.sleep_seconds):
                break
