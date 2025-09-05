from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db import connection
from mastery.imports.task_tracker import run_with_task_tracking, import_groups_and_users
from mastery.imports.feide_api import (
    fetch_feide_groups_for_school_and_store,
    fetch_feide_users_for_school_and_store,
)
from mastery.imports.school_importer import import_school_from_feide
from django.db.models import Q


from mastery import models


# Used by frontend to check status of API and DB
@api_view(["GET"])
@permission_classes([AllowAny])
def ping(request):
    db_status = "unknown"
    http_status = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = "up"
    except Exception:
        db_status = "down"
        http_status = 503
    return Response({"api": "up", "db": db_status}, status=http_status)


def _get_flag(data, key, default=False):
    v = data.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in {"1", "true", "t", "yes", "on", "y"}
    if isinstance(v, int):
        return v != 0
    return default


def _check_superadmin(request):
    if not request.user.is_superadmin:
        return Response(
            {"status": "error", "message": "Only superadmins can access this endpoint"},
            status=403,
        )
    return None


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def feide_import_school_api(request, org_number):
    """
    Import a single school by org number from Feide and create/update in our database.
    """
    admin_check = _check_superadmin(request)
    if admin_check:
        return admin_check

    try:
        result = run_with_task_tracking(
            job_name="feide_import_school",
            target_id=org_number,
            func=import_school_from_feide,
            org_number=org_number,
        )

        import_result = result.get("step_results", {})
        print("Import result:", import_result)

        if import_result.get("status") == "not_found":
            return Response(
                {"status": "error", "message": "Feide group not found"}, status=404
            )

        return Response(
            {
                "status": "success",
                "message": f"School {import_result.get('display_name', org_number)} imported successfully",
                "school": import_result,
                "task_id": result.get("task_id"),
            }
        )

    except Exception as e:
        return Response(
            {"status": "error", "message": f"Failed to import school: {str(e)}"},
            status=400,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def feide_fetch_groups_for_school_api(request, org_number):
    """
    Fetch Feide groups for a single school (by org number) and store them
    at imports/data/schools/<org>/groups.json. Returns simple counts.
    """
    admin_check = _check_superadmin(request)
    if admin_check:
        return admin_check

    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number

        result = run_with_task_tracking(
            job_name="fetch_feide_groups_for_school",
            target_id=target,
            func=fetch_feide_groups_for_school_and_store,
            org_number=org_number,
        )
        return Response({"status": "success", **result})
    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": f"Failed to fetch groups for org {org_number}: {str(e)}",
            },
            status=400,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def feide_fetch_users_for_school_api(request, org_number):
    """
    Fetch users/memberships for a single school (by org number) into imports/data/schools/<org>/users.json
    """
    admin_check = _check_superadmin(request)
    if admin_check:
        return admin_check
    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number
        result = run_with_task_tracking(
            job_name="fetch_feide_users_for_school_and_store",
            target_id=target,
            func=fetch_feide_users_for_school_and_store,
            org_number=org_number,
        )
        return Response({"status": "success", **result})
    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": f"Failed to fetch users for org {org_number}: {str(e)}",
            },
            status=400,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def import_groups_and_users_api(request, org_number):
    """
    Import groups and users for a specific school from previously fetched files.
    """
    admin_check = _check_superadmin(request)
    if admin_check:
        return admin_check
    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number

        is_overwrite_enabled = _get_flag(request.data, "is_overwrite_enabled", False)
        is_crash_on_error_enabled = _get_flag(
            request.data, "is_crash_on_error_enabled", False
        )

        result = run_with_task_tracking(
            job_name="import_groups_and_users",
            target_id=target,
            func=import_groups_and_users,
            org_number=org_number,
            is_overwrite_enabled=is_overwrite_enabled,
            is_crash_on_error_enabled=is_crash_on_error_enabled,
        )

        return Response(
            {
                "status": "success",
                "message": f"Import of groups and users completed for school {target}",
                "org_number": org_number,
                **result,
            }
        )
    except Exception as e:
        return Response(
            {
                "status": "error",
                "message": f"Import of groups and users failed: {str(e)}",
                "org_number": org_number,
            },
            status=500,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def fetch_school_import_status_api(request, org_number):
    """
    Return status for one school:
    - Groups: last fetch count + time, DB count, diff
    - Users:  last fetch count + time, DB count, diff
    - Memberships: DB count, diff
    - Last import timestamp
    """
    admin_check = _check_superadmin(request)
    if admin_check:
        return admin_check

    school = models.School.objects.filter(org_number=org_number).first()

    # Tasks target id filter
    target_filter = Q(target_id=org_number)
    if school and school.display_name:
        target_filter |= Q(target_id=school.display_name)

    # Latest finished tasks
    last_groups_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="fetch_feide_groups_for_school", status="finished")
        .filter(target_filter)
        .order_by("-finished_at")
        .first()
    )
    last_users_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="fetch_feide_users_for_school_and_store", status="finished")
        .filter(target_filter)
        .order_by("-finished_at")
        .first()
    )
    last_import_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="import_groups_and_users", status="finished")
        .filter(target_filter)
        .order_by("-finished_at")
        .first()
    )

    # Extract fetched counts and timestamps
    groups_fetched_count = (last_groups_task.result or {}).get("total_groups") if last_groups_task else None
    users_fetched_count = (last_users_task.result or {}).get("unique_users") if last_users_task else None
    memebership_fetched_count = (last_users_task.result or {}).get(
        "total_memberships") if last_users_task else None

    groups_fetched_at = last_groups_task.finished_at.isoformat(
    ) if last_groups_task and last_groups_task.finished_at else None
    users_fetched_at = last_users_task.finished_at.isoformat(
    ) if last_users_task and last_users_task.finished_at else None
    last_import_at = last_import_task.finished_at.isoformat(
    ) if last_import_task and last_import_task.finished_at else None

    # DB counts
    if school:
        groups_db_count = models.Group.objects.filter(
            school=school, type__in=["basis", "teaching"]
        ).count()
        users_db_count = models.User.objects.filter(
            groups__school=school
        ).distinct().count()
        user_groups_db_count = models.UserGroup.objects.filter(
            group__school=school
        ).count()
    else:
        groups_db_count = 0
        users_db_count = 0
        user_groups_db_count = 0

    # Diffs
    groups_diff = (groups_fetched_count - groups_db_count) if isinstance(groups_fetched_count, int) else None
    users_diff = (users_fetched_count - users_db_count) if isinstance(users_fetched_count, int) else None
    user_groups_diff = (
        memebership_fetched_count - user_groups_db_count) if isinstance(memebership_fetched_count, int) else None

    return Response({
        "status": "success",
        "orgNumber": org_number,
        "school": {
            "id": getattr(school, "id", None),
            "displayName": getattr(school, "display_name", None),
        },
        "groups": {
            "fetchedCount": groups_fetched_count,
            "fetchedAt": groups_fetched_at,
            "dbCount": groups_db_count,
            "diff": groups_diff,
        },
        "users": {
            "fetchedCount": users_fetched_count,
            "fetchedAt": users_fetched_at,
            "dbCount": users_db_count,
            "diff": users_diff,
        },
        "memberships": {
            "fetchedCount": memebership_fetched_count,
            "dbCount": user_groups_db_count,
            "diff": user_groups_diff,
        },
        "lastImportAt": last_import_at,
    })
