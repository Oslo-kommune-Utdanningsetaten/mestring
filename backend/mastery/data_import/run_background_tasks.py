from mastery.data_import.feide_api import fetch_groups_from_feide, fetch_memberships_from_feide
import names
import time
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from mastery.models import DataMaintenanceTask, generate_nanoid
from .import_school import school_update
from .import_groups import import_groups_from_file
from .import_users import import_memberships_from_file

# Retries after initial attempt. Retry in 1, 3, 10 minutes before giving up.
RETRY_BACKOFF = [1*60, 3*60, 10*60]


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
        task.handler_name = f"{names.get_full_name()} {generate_nanoid(size=6)}"
        task.attempts = task.attempts + 1
        task.save(update_fields=["status", "started_at", "handler_name",
                  "last_heartbeat_at", "attempts", "updated_at"])
        return task


# For each chunk of work done, update the progress
def update_progress(task, result):
    DataMaintenanceTask.objects.filter(id=task.id).update(result=result, last_heartbeat_at=timezone.now())


def next_execution_time(task):
    delay = RETRY_BACKOFF[task.attempts - 1]
    return timezone.now() + timedelta(seconds=delay)


def append_error_to_result(task, error):
    result = task.result or {}
    errors = result.get("errors", [])
    errors.append({"error": "unexpected-error", "message": str(error)[:1000]})
    result["errors"] = errors
    return result


def do_work(task):
    '''
    The yield from do_work(task) MUST produce dicts on this format:
    {
        "result": {
            "entity": "school",
            "action": "update",
            "total_count": iterations,
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": [{error: "...", message: "..."}],
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
    else:
        raise ValueError(f"Unknown job_name '{task.job_name}'")


# Used when running as long-lived process
def run_indefinitely():
    while True:
        run()
        time.sleep(2)


# Used on manual one-off tasks, or in tests
def run():
    task = claim_next_task()
    if task:
        try:
            # do work in chunks, update result
            for chunk in do_work(task):
                update_progress(task, chunk.get("result"))
                if chunk.get("is_done"):
                    break
            task.refresh_from_db(fields=["result"])
            task.status = "finished"
            task.finished_at = timezone.now()
            task.save(update_fields=["status", "finished_at", "updated_at"])
        except Exception as error:
            with transaction.atomic():
                # refresh task to avoid stale data
                fresh_task = (DataMaintenanceTask.objects.select_for_update().only(
                    "id", "result", "attempts", "status", "handler_name", "earliest_run_at", "updated_at",
                    "failed_at").get(id=task.id))
                # append error to result
                fresh_task.result = append_error_to_result(fresh_task, error)

                if fresh_task.attempts <= len(RETRY_BACKOFF):
                    # failed, but schedule retry
                    fresh_task.status = "pending"
                    fresh_task.handler_name = None
                    fresh_task.failed_at = None
                    fresh_task.earliest_run_at = next_execution_time(fresh_task)
                else:
                    # failed, no more retries
                    fresh_task.status = "failed"
                    fresh_task.failed_at = timezone.now()
                    fresh_task.earliest_run_at = None

                fresh_task.save(update_fields=[
                    "result", "attempts", "status", "handler_name",
                    "earliest_run_at", "failed_at", "updated_at"
                ])
        return task
    return None
