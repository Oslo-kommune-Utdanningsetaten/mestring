
import pytest
from django.utils import timezone
from mastery.models import DataMaintenanceTask
from backend.mastery.data_import import run_background_tasks


@pytest.fixture
def groups_fetch_task(db):
    return DataMaintenanceTask.objects.create(
        status="pending",
        job_name="fetch_groups_from_feide",
        job_params={"org_number": "NO123456789"},
        display_name=f"Fetch groups for skole NO123456789",
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
def test_group_fetch(groups_fetch_task):
    run_background_tasks.run()
    groups_fetch_task.refresh_from_db()
    assert groups_fetch_task.status == 'finished'
    assert len(groups_fetch_task.result['errors']) == 0
