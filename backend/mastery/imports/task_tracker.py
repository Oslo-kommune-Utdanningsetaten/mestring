from django.utils import timezone
from django.db import transaction, close_old_connections
from mastery import models

def run_with_task_tracking(job_name, target_id, func, is_dryrun_enabled=False, is_crash_on_error_enabled=False, is_overwrite_enabled=False, *args, **kwargs):
    """Run a function with DataMaintenanceTask tracking, supporting dry run."""
    # Create task record
    task = models.DataMaintenanceTask.objects.create(
        job_name=job_name,
        target_id=target_id,
        status='pending',
        result={},
        is_dryrun_enabled=is_dryrun_enabled,
        is_crash_on_error_enabled=is_crash_on_error_enabled,
        is_overwrite_enabled=is_overwrite_enabled
    )

    print(f"📋 Starting task: {job_name} (ID: {task.id})")
    if is_overwrite_enabled:
        print("⚠️ Overwrite enabled: Existing data may be replaced.")

    task.status = 'running'
    task.started_at = timezone.now()
    task.save()

    try:
        if is_dryrun_enabled:
            # Dry run: run in atomic block and force rollback
            with transaction.atomic():
                result = func(*args, **kwargs)
                print(f"✅ Dry run completed: {job_name} (ID: {task.id})")
                transaction.set_rollback(True)
            # Mark dryrun as finished after running
            task.status = 'finished'
            task.finished_at = timezone.now()
            task.result = {'dryrun': True, 'preview': result}
            task.save()
            return {
                'task_id': str(task.id),
                'step_results': {'dryrun': True, 'preview': result}
            }
        else:
            # Normal run: commit changes
            with transaction.atomic():
                result = func(*args, **kwargs)
                
            # Update task status OUTSIDE the transaction
            task.status = 'finished'
            task.finished_at = timezone.now()
            task.result = result
            task.save()
            print(f"✅ Task completed: {job_name} (ID: {task.id})")
            return {
                'task_id': str(task.id),
                'step_results': result if isinstance(result, dict) else {'result': result}
            }

    except Exception as e:
        # Close old connections to get a fresh connection
        close_old_connections()
        
        if is_crash_on_error_enabled:
            print(f"❌ Task crashed on error: {job_name} (ID: {task.id}) - {e}")
            raise
        else:
            task.status = 'failed'
            task.failed_at = timezone.now()
            task.result = {'error': str(e)}
            task.save()
            print(f"❌ Task failed: {job_name} (ID: {task.id}) - {e}")
            raise e