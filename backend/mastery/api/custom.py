from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.utils import extend_schema, OpenApiParameter
from mastery.data_import.import_school import import_school_from_feide
from mastery.data_import.helpers import get_school_fetched_stats
from mastery.access_policies import ImportAccessPolicy
from mastery import models


# Used by frontend to check status of API and DB
@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie  # Hand out CSRF cookie to the client
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


@extend_schema(
    operation_id="feide_import_school",
    summary="Import school from Feide",
    description="Import a single school by org number from Feide and create/update in our database.",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Import a single school by org number from Feide and create/update in our database.',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["POST"])
@permission_classes([ImportAccessPolicy])
def import_school(request, org_number):
    """
    Import a single school by org number from Feide and create/update in our database.
    """
    try:
        import_school_from_feide(org_number)
        return Response(
            {
                "status": "success",
                "message": f"School with org number {org_number} imported/updated successfully",
            },
            status=201,
        )
    except Exception as e:
        return Response(
            {"status": "error", "message": f"Failed to import school: {str(e)}"},
            status=400,
        )


@extend_schema(
    operation_id="fetch_groups_for_school",
    summary="Fetch groups for school",
    description="Fetch Feide groups for a single school (by org number) and store them at data_import/data/schools/<org>/groups.json. Returns simple counts.",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Organization number of the school',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["POST"])
@permission_classes([ImportAccessPolicy])
def fetch_groups_for_school(request, org_number):
    """
    Fetch Feide groups for a single school (by org number) and store them
    at data_import/data/schools/<org>/groups.json. Returns simple counts.
    """
    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        return Response(
            {"status": "error", "message": f"School not found for org {org_number}"},
            status=404,
        )

    # Check if there's already a pending or running task for this job and org_number
    existing_task = models.DataMaintenanceTask.objects.filter(
        Q(status="pending") | Q(status="running"),
        job_name="fetch_groups_from_feide",
        job_params__org_number=org_number
    ).first()
    if existing_task:
        return Response(
            {"status": "error", "message": "A fetch groups task is already pending or running for this school."},
            status=409,
        )

    task = models.DataMaintenanceTask.objects.create(
        status="pending",
        job_name="fetch_groups_from_feide",
        job_params={"org_number": org_number},
        display_name=f"Fetch groups for {school.display_name}",
        earliest_run_at=timezone.now()
    )
    return Response(status=201, data={"status": "task_created", "task_id": task.id})


@extend_schema(
    operation_id="fetch_memberships_for_school",
    summary="Fetch group memberships for school",
    description="Fetch group memberships for a single school (by org number) and store at data_import/data/schools/<org>/users.json",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Organization number of the school',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["POST"])
@permission_classes([ImportAccessPolicy])
def fetch_memberships_for_school(request, org_number):
    """
    Fetch all group memberships for a single school (by org number) into data_import/data/schools/<org>/memberships.json
    """
    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        return Response(
            {"error": "unknown-school", "message": f"School not found for org {org_number}"},
            status=404,
        )

    # Check if there's already a pending or running task for this job and org_number
    existing_task = models.DataMaintenanceTask.objects.filter(
        Q(status="pending") | Q(status="running"),
        job_name="fetch_memberships_from_feide",
        job_params__org_number=org_number
    ).first()
    if existing_task:
        return Response(
            {"status": "error",
             "message": "A fetch memberships task is already pending or running for this school."},
            status=409,)

    task = models.DataMaintenanceTask.objects.create(
        status="pending",
        job_name="fetch_memberships_from_feide",
        job_params={"org_number": org_number},
        display_name=f"Fetch memberships for {school.display_name}",
        earliest_run_at=timezone.now()
    )
    return Response(status=201, data={"status": "task_created", "task_id": task.id})


@extend_schema(
    operation_id="import_groups_and_users",
    summary="Import groups and users",
    description="Import groups and users for a specific school from previously fetched files.",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Organization number of the school',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["POST"])
@permission_classes([ImportAccessPolicy])
def import_groups_and_users(request, org_number):
    """
    Import groups and users for a specific school from previously fetched files.
    """
    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        return Response(
            {"error": "unknown-school", "message": f"School not found for org {org_number}"},
            status=404,
        )

    # Check if there's already a pending or running task for this job and org_number
    existing_task = models.DataMaintenanceTask.objects.filter(
        Q(status="pending") | Q(status="running"),
        job_name__in=["import_groups", "import_memberships"],
        job_params__org_number=org_number
    ).first()
    if existing_task:
        return Response(
            {"status": "error",
             "message": "An import groups or memberships task is already pending or running for this school."},
            status=409,)

    task = models.DataMaintenanceTask.objects.create(
        status="pending",
        job_name="import_groups",
        job_params={"org_number": org_number},
        display_name=f"Import groups for {school.display_name}",
        earliest_run_at=timezone.now()
    )
    task2 = models.DataMaintenanceTask.objects.create(
        status="pending",
        job_name="import_memberships",
        job_params={"org_number": org_number},
        display_name=f"Import memberships for {school.display_name}",
        earliest_run_at=timezone.now()
    )
    return Response(status=201, data={"status": "tasks_created", "task_ids": [task.id, task2.id]})


@extend_schema(
    operation_id="update_data_integrity",
    summary="Ensure data integrity is as expected",
    description="Soft-delete data which has not been maintained during imports, and hard-delete data which has been soft-deleted for a sufficient time.",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Organization number of the school',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["POST"])
@permission_classes([ImportAccessPolicy])
def update_data_integrity(request, org_number):
    """
    Activate the cleaner bot.
    """
    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        return Response(
            {"message": f"School not found for org {org_number}"},
            status=404,
        )
    # Check if there's already a pending or running similar task
    existing_task = models.DataMaintenanceTask.objects.filter(
        Q(status="pending") | Q(status="running"),
        job_name="update_data_integrity",
    ).first()
    if existing_task:
        return Response(
            {"status": "error",
             "message": "Another cleaner bot is already pending or running."},
            status=409)

    task = models.DataMaintenanceTask.objects.create(
        status="pending",
        job_name="update_data_integrity",
        job_params={"maintained_earlier_than": timezone.now()},
        display_name=f"Activate cleaner bot",
        earliest_run_at=timezone.now()
    )
    return Response(status=201, data={"status": "tasks_created", "task_ids": [task.id]})


@extend_schema(
    operation_id="fetch_school_import_status",
    summary="Get school import status",
    description="Return status for one school: Groups, Users, Memberships (last fetch count + time, DB count, diff) and last import timestamp.",
    parameters=[
        OpenApiParameter(
            name='org_number',
            description='Organization number of the school',
            required=True,
            type={'type': 'string'},
            location=OpenApiParameter.PATH
        )
    ]
)
@api_view(["GET"])
@permission_classes([ImportAccessPolicy])
def fetch_school_import_status(request, org_number):
    """
    Return status for one school:
    - Groups: last fetch count + time, DB count, diff
    - Users:  last fetch count + time, DB count, diff
    - Memberships: DB count, diff
    - Last import timestamp
    """

    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        return Response(
            {"message": f"School not found for org {org_number}"},
            status=404,
        )

    fetched_stats = get_school_fetched_stats(org_number)

    # Latest finished tasks (for timestamps only)
    last_groups_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="fetch_groups_from_feide", status="finished")
        .filter(job_params__org_number=org_number)
        .order_by("-finished_at")
        .first()
    )
    last_users_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="fetch_memberships_from_feide", status="finished")
        .filter(job_params__org_number=org_number)
        .order_by("-finished_at")
        .first()
    )
    last_import_task = (
        models.DataMaintenanceTask.objects
        .filter(job_name="import_groups_and_users", status="finished")
        .filter(job_params__org_number=org_number)
        .order_by("-finished_at")
        .first()
    )

    # Extract timestamps from finished_at field
    groups_fetched_at = last_groups_task.finished_at.isoformat(
    ) if last_groups_task and last_groups_task.finished_at else None
    users_fetched_at = last_users_task.finished_at.isoformat(
    ) if last_users_task and last_users_task.finished_at else None
    last_import_at = last_import_task.finished_at.isoformat(
    ) if last_import_task and last_import_task.finished_at else None

    # DB counts
    groups_db_count = models.Group.objects.filter(
        school=school, type__in=["basis", "teaching"]
    ).count()
    users_db_count = models.User.objects.filter(
        groups__school=school
    ).distinct().count()
    user_groups_db_count = models.UserGroup.objects.filter(
        group__school=school
    ).count()

    # Calculate diffs using helper data
    groups_diff = (
        fetched_stats['groups_count'] - groups_db_count) if isinstance(fetched_stats['groups_count'], int) else None
    users_diff = (
        fetched_stats['users_count'] - users_db_count) if isinstance(fetched_stats['users_count'], int) else None
    user_groups_diff = (
        fetched_stats['memberships_count'] - user_groups_db_count) if isinstance(
        fetched_stats['memberships_count'],
        int) else None

    return Response({
        "orgNumber": org_number,
        "school": {
            "id": school.id,
            "displayName": school.display_name,
        },
        "groups": {
            "fetchedCount": fetched_stats['groups_count'],
            "fetchedAt": groups_fetched_at,
            "dbCount": groups_db_count,
            "diff": groups_diff,
        },
        "users": {
            "fetchedCount": fetched_stats['users_count'],
            "fetchedAt": users_fetched_at,
            "dbCount": users_db_count,
            "diff": users_diff,
        },
        "memberships": {
            "fetchedCount": fetched_stats['memberships_count'],
            "dbCount": user_groups_db_count,
            "diff": user_groups_diff,
        },
        "lastImportAt": last_import_at,
    })
