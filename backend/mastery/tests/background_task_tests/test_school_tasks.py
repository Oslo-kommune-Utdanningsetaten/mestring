
import pytest
from django.utils import timezone
from mastery.models import DataMaintenanceTask
from mastery.data_import import background_task_handler


@pytest.fixture
def school_update_task(db):
    return DataMaintenanceTask.objects.create(
        status="pending",
        job_name="update_schools",
        job_params={"org_number": "NO123456789"},
        display_name="Update school names for org NO123456789",
        is_overwrite_enabled=True,
        is_crash_on_error_enabled=False,
        earliest_run_at=timezone.now()
    )


@pytest.fixture
def school_update_task_with_wrong_job_name(db):
    return DataMaintenanceTask.objects.create(
        status="pending",
        job_name="NO_SUCH_JOB",
        job_params={"org_number": "NO123456789"},
        display_name="Update school names for org NO123456789",
        earliest_run_at=timezone.now()
    )


@pytest.mark.django_db
def test_school_update(school_update_task):
    background_task_handler.run()
    school_update_task.refresh_from_db()
    assert school_update_task.status == "finished"

    result = school_update_task.result
    assert result["key"] == "school-update"
    assert result["entity"] == "school"
    assert result["action"] == "update"
    assert result["total_count"] == 1000
    assert result["success_count"] + result["failure_count"] == 1000
    assert len(result["errors"]) == 0


@pytest.mark.django_db
def test_school_update_does_not_run_with_wrong_job_name(school_update_task_with_wrong_job_name):
    background_task_handler.run()
    school_update_task_with_wrong_job_name.refresh_from_db()
    assert school_update_task_with_wrong_job_name.status == "pending"
    result = school_update_task_with_wrong_job_name.result
    assert len(result["errors"]) == 1
    assert result["errors"][0]["error"] == "unexpected-error"
    assert "Unknown job_name" in result["errors"][0]["message"]


@pytest.mark.django_db
def test_future_task_not_claimed(db):
    # earliest_run_at in the future should not be claimed/run
    future_time = timezone.now() + timezone.timedelta(minutes=5)
    task = DataMaintenanceTask.objects.create(
        status="pending",
        job_name="update_schools",
        job_params={"org_number": "NO999"},
        display_name="Should not run yet",
        earliest_run_at=future_time,
    )
    returned = background_task_handler.run()
    task.refresh_from_db()
    assert returned is None  # nothing ran
    assert task.status == "pending"
    assert task.attempts == 0  # still not attempted
    assert task.handler_name is None  # still not claimed


@pytest.mark.django_db
def test_unknown_job_schedules_retry(db):
    task = DataMaintenanceTask.objects.create(
        status="pending",
        job_name="NO_SUCH_JOB",
        job_params={"org_number": "NO123"},
        display_name="Bad job triggers retry",
        earliest_run_at=timezone.now(),
    )
    background_task_handler.run()
    task.refresh_from_db()
    # after first failed attempt we should schedule a retry
    assert task.status == "pending"
    assert task.attempts == 1
    assert task.handler_name is None  # cleared for retry
    assert task.earliest_run_at is not None and task.earliest_run_at > timezone.now()
    assert task.result and len(task.result.get("errors", [])) == 1


@pytest.mark.django_db
def test_unknown_job_exceeds_retries_and_fails(db):
    # Pre-set attempts to max retries so next failure exhausts retries
    max_retries = len(background_task_handler.RETRY_BACKOFF)
    task = DataMaintenanceTask.objects.create(
        status="pending",
        job_name="NO_SUCH_JOB",
        job_params={"org_number": "NO123"},
        display_name="Bad job exceeds retries",
        earliest_run_at=timezone.now(),
        attempts=max_retries,  # will become max_retries+1 when claimed
    )
    background_task_handler.run()
    task.refresh_from_db()
    assert task.status == "failed"
    assert task.attempts == max_retries + 1
    assert task.failed_at is not None
    assert task.earliest_run_at is None  # no further retries
    # handler_name should remain set from the final attempt
    assert task.handler_name is not None
    assert task.result and len(task.result.get("errors", [])) >= 1


@pytest.mark.django_db
def test_success_task_sets_handler_and_timestamps(school_update_task):
    background_task_handler.run()
    school_update_task.refresh_from_db()
    assert school_update_task.status == "finished"
    assert school_update_task.attempts == 1
    assert school_update_task.handler_name is not None
    assert school_update_task.started_at is not None
    assert school_update_task.finished_at is not None
    assert school_update_task.last_heartbeat_at is not None
    assert school_update_task.started_at <= school_update_task.last_heartbeat_at <= school_update_task.finished_at
    # ensure progress result looks final (is done) by checking counts sum to total
    result = school_update_task.result
    assert result["success_count"] + result["failure_count"] == result["total_count"]
