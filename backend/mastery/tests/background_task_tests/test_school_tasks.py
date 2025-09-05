
import pytest
from django.utils import timezone
from mastery.models import DataMaintenanceTask
from mastery.imports import background_task_handler


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
