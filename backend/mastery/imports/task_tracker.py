from django.utils import timezone
from django.db import close_old_connections
from .group_importer import import_groups_from_file
from .user_importer import import_users_from_file
from .helpers import check_school_data_status
from mastery import models
import inspect


def run_with_task_tracking(
    job_name,
    target_id,
    func,
    is_dryrun_enabled=False,
    is_crash_on_error_enabled=False,
    is_overwrite_enabled=False,
    *args,
    **kwargs,
):
    """
    Run a function with DataMaintenanceTask tracking.
    """
    # Create task
    task = models.DataMaintenanceTask.objects.create(
        job_name=job_name,
        target_id=target_id,
        status="pending",
        result={},
        is_dryrun_enabled=is_dryrun_enabled,
        is_crash_on_error_enabled=is_crash_on_error_enabled,
        is_overwrite_enabled=is_overwrite_enabled,
    )
    print(f"📋 Starting task: {job_name} (ID: {task.id})")
    if is_overwrite_enabled:
        print("⚠️ Overwrite enabled: existing data may be replaced.")
    if is_dryrun_enabled:
        print("🧪 DRY RUN enabled: no database writes will be performed.")

    # Move to running
    task.status = "running"
    task.started_at = timezone.now()
    task.save()

    _forward_supported_flags(
        func,
        kwargs,
        is_dryrun_enabled=is_dryrun_enabled,
        is_overwrite_enabled=is_overwrite_enabled,
        is_crash_on_error_enabled=is_crash_on_error_enabled,
    )

    try:
        # Let the function manage its own (short) transactions per step if needed.
        result = func(*args, **kwargs)

        # Finish
        task.status = "finished"
        task.finished_at = timezone.now()
        task.result = result if isinstance(result, dict) else {"result": result}
        task.save()
        print(f"✅ Task completed: {job_name} (ID: {task.id})")
        if is_dryrun_enabled:
            print("🧪 DRY RUN: no changes were made to the database.")

        duration_s = (
            (task.finished_at - task.started_at).total_seconds()
            if task.started_at and task.finished_at
            else None
        )

        # FIXED: Use snake_case consistently
        return {
            "task_id": str(task.id),
            "job": job_name,
            "target": target_id,
            "started_at": task.started_at.isoformat(),
            "finished_at": task.finished_at.isoformat(),
            "duration": duration_s,
            "flags": {
                "dry_run": is_dryrun_enabled,
                "overwrite": is_overwrite_enabled,
                "crash_on_error": is_crash_on_error_enabled,
            },
            "step_results": task.result,
        }

    except Exception as e:
        # Refresh connection if needed
        close_old_connections()

        # Mark failed
        task.status = "failed"
        task.failed_at = timezone.now()
        task.result = {"error": str(e)}
        task.save()
        print(f"❌ Task failed: {job_name} (ID: {task.id}) - {e}")

        if is_crash_on_error_enabled:
            raise
        raise e


def _forward_supported_flags(
    func, kwargs, *, is_dryrun_enabled, is_overwrite_enabled, is_crash_on_error_enabled
):
    """Only pass flags the function actually accepts."""
    params = inspect.signature(func).parameters
    if "is_dryrun_enabled" in params and "is_dryrun_enabled" not in kwargs:
        kwargs["is_dryrun_enabled"] = is_dryrun_enabled
    if "is_overwrite_enabled" in params and "is_overwrite_enabled" not in kwargs:
        kwargs["is_overwrite_enabled"] = is_overwrite_enabled
    if (
        "is_crash_on_error_enabled" in params
        and "is_crash_on_error_enabled" not in kwargs
    ):
        kwargs["is_crash_on_error_enabled"] = is_crash_on_error_enabled


def import_groups_and_users(
    org_number,
    is_overwrite_enabled=False,
    is_dryrun_enabled=False,
    is_crash_on_error_enabled=False,
):
    results = {}

    status = check_school_data_status(org_number)
    if not status["groups_file_exists"]:
        raise Exception(
            f"No groups file found for school {org_number}. Fetch groups first."
        )
    if not status["users_file_exists"]:
        raise Exception(
            f"No users file found for school {org_number}. Fetch users first."
        )

    if org_number:
        print(f"🔄 Importing groups for school {org_number}...")
        groups_result = import_groups_from_file(
            org_number,
            is_overwrite_enabled=is_overwrite_enabled,
            is_dryrun_enabled=is_dryrun_enabled,
        )
        users_result = import_users_from_file(
            org_number,
            is_overwrite_enabled=is_overwrite_enabled,
            is_dryrun_enabled=is_dryrun_enabled,
        )
        results["groups"] = groups_result
        results["users"] = users_result
        print(f"✅ Groups and users import completed for school {org_number}.")
    else:
        print("⚠️ No org_number provided, skipping groups import")
        results["groups"] = {"message": "Skipped - no org_number provided"}

    return results


# TODO: Futrue proofing when we want to sync school data automatically

# def _build_import_workflow(org_number: str):
#     """Plan minimal steps per school."""
#     status = check_school_data_status(org_number)
#     workflow = ["import_school"]

#     if not status["groups_file_exists"]:
#         workflow.append("fetch_groups")
#     if not status["users_file_exists"]:
#         workflow.append("fetch_users")

#     workflow.append("import_groups")
#     workflow.append("import_users")

#     return workflow, status


# def sync_school_data(
#     org_number: str,
#     is_overwrite_enabled: bool = False,
#     is_dryrun_enabled: bool = False,
# ):
#     """
#     Synchronize one school, per-school only:
#     - import_school (upsert from Feide)
#     - fetch_groups (if missing) -> import_groups
#     - fetch_users  (if missing) -> import_users
#     """
#     workflow, initial_status = _build_import_workflow(org_number)
#     results = {
#         "initial_status": initial_status,
#         "steps_executed": [],
#         "step_results": {},
#     }

#     print(f"🧠 Sync school for {org_number}")
#     print(f"📋 Planned workflow: {' → '.join(workflow)}")

#     for step in workflow:
#         print(f"\n🔄 Executing: {step}")
#         if step == "import_school":
#             result = import_school_from_feide(org_number)
#         elif step == "fetch_groups":
#             result = fetch_and_store_feide_groups_for_school(org_number)
#         elif step == "fetch_users":
#             result = fetch_feide_users_for_school(org_number)
#         elif step == "import_groups":
#             result = import_groups_from_file(
#                 org_number,
#                 is_overwrite_enabled=is_overwrite_enabled,
#                 is_dryrun_enabled=is_dryrun_enabled,
#             )
#         elif step == "import_users":
#             result = import_users_from_file(
#                 org_number,
#                 is_overwrite_enabled=is_overwrite_enabled,
#                 is_dryrun_enabled=is_dryrun_enabled,
#             )
#         else:
#             result = {"message": f"Unknown step: {step}"}

#         results["steps_executed"].append(step)
#         results["step_results"][step] = result

#     return results
