# import os
import sys
from .task_tracker import run_with_task_tracking
from .feide_api import fetch_and_store_feide_groups, fetch_feide_users
from .school_importer import import_schools_from_file
from .group_importer import import_groups_from_file
from .user_importer import import_users_from_file
from .helpers import check_school_data_status


def _build_import_workflow(org_number):
    """Determine what operations are needed"""
    status = check_school_data_status(org_number)
    workflow = []
    if not status["groups_file_exists"]:
        print(f"⚠️  NOTICE: Groups data missing for school {org_number}")
        print("   This will require fetching ALL school groups (2-5 minutes)")
        workflow.append("fetch_groups")
    workflow.append("import_groups")
    if not status["users_file_exists"]:
        workflow.append("fetch_users")
    workflow.append("import_users")
    return workflow, status


def sync_school_data(org_number, is_overwrite_enabled=False, is_dryrun_enabled=False):
    """
    Synchronize one school data: plan steps based on available files (fetch if missing),
    then import schools, groups, users in order.
    """
    workflow, initial_status = _build_import_workflow(org_number)
    results = {
        'initial_status': initial_status,
        'steps_executed': [],
        'step_results': {}
    }
    print(f"🧠 Sync school for school {org_number}")
    print(f"📋 Planned workflow: {' → '.join(workflow)}")
    for step in workflow:
        print(f"\n🔄 Executing: {step}")
        if step == 'fetch_groups':
            result = fetch_and_store_feide_groups()
        elif step == 'fetch_users':
            result = fetch_feide_users(org_number)
        elif step == 'import_schools':
            result = import_schools_from_file(
                org_number, is_overwrite_enabled=is_overwrite_enabled, is_dryrun_enabled=is_dryrun_enabled
            )
        elif step == 'import_groups':
            result = import_groups_from_file(
                org_number, is_overwrite_enabled=is_overwrite_enabled, is_dryrun_enabled=is_dryrun_enabled
            )
        elif step == 'import_users':
            result = import_users_from_file(
                org_number, is_overwrite_enabled=is_overwrite_enabled, is_dryrun_enabled=is_dryrun_enabled
            )
        results['steps_executed'].append(step)
        results['step_results'][step] = result
    return results


def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        org_number = sys.argv[2] if len(sys.argv) > 2 else None
        if command == "fetch":
            run_with_task_tracking("fetch_groups", None, fetch_and_store_feide_groups)
        elif command == "import-schools":
            run_with_task_tracking(
                job_name="import_schools",
                target_id=None,
                func=import_schools_from_file,
                is_crash_on_error_enabled=True,
                is_dryrun_enabled=True,
            )
        elif command == "sync-school":
            if not org_number:
                print("❌ Usage: python -m mastery.imports sync-school <org_number>")
            else:
                run_with_task_tracking(
                    job_name="sync_school_data",
                    target_id=org_number,
                    func=sync_school_data,
                    is_dryrun_enabled=True,
                    org_number=org_number,
                )
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python -m mastery.imports' to see available commands")
    else:
        print("📋 Available commands:")
        print("  fetch                      - Fetch groups from Feide")
        print("  sync-school <org_number>  - Sync school for a specific school")
        print("  python -m mastery.imports fetch")
        print("  python -m mastery.imports sync-school NO975291146")
