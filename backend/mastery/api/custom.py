from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection
from mastery.imports.task_tracker import run_with_task_tracking,import_groups_and_users
from mastery.imports.feide_api import fetch_and_store_feide_groups_for_school, fetch_feide_users_for_school
from mastery.imports.school_importer import import_school_from_feide


from mastery import models

# Used by frontend to check status of API and DB
@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    db_status = 'unknown'
    http_status = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = 'up'
    except Exception:
        db_status = 'down'
        http_status = 503
    return Response({"api": "up", "db": db_status}, status=http_status)

def _get_flag(data, key, default=False):
    v = data.get(key, default)
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        return v.lower() in {"1","true","t","yes","on","y"}
    if isinstance(v, int):
        return v != 0
    return default


@api_view(['POST'])
@permission_classes([AllowAny])
def feide_import_school_api(request, org_number):
    """
    Import a single school by org number from Feide and create/update in our database.
    """
    try:
        # Use task tracking like the other endpoints
        result = run_with_task_tracking(
            job_name='feide_import_school',
            target_id=org_number,
            func=import_school_from_feide,
            org_number=org_number,
        )
        
        # Extract the actual result from stepResults (camelCase from task tracker)
        import_result = result.get('step_results', {})
        print("Import result:", import_result)
        
        if import_result.get('status') == 'not_found':
            return Response({
                "status": "error", 
                "message": "Feide group not found"
            }, status=404)
            
        return Response({
            "status": "success",
            "message": f"School {import_result.get('display_name', org_number)} imported successfully",
            "school": import_result,
            "task_id": result.get('task_id')
        })
        
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to import school: {str(e)}"
        }, status=400)
    

@api_view(['GET'])
@permission_classes([AllowAny])
def feide_fetch_groups_for_school_api(request, org_number):
    """
    Fetch Feide groups for a single school (by org number) and store them
    at imports/data/schools/<org>/groups.json. Returns simple counts.
    """
    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number

        result = run_with_task_tracking(
            job_name='fetch_feide_groups_for_school',
            target_id=target,
            func=fetch_and_store_feide_groups_for_school,           
            org_number= org_number,  
        )
        return Response({"status": "success", **result})
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to fetch groups for org {org_number}: {str(e)}"
        }, status=400)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def feide_fetch_users_for_school_api(request, org_number):
    """
    Fetch users/memberships for a single school (by org number) into imports/data/schools/<org>/users.json
    """
    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number
        result = run_with_task_tracking(
            job_name='fetch_feide_users_for_school',
            target_id=target,
            func=fetch_feide_users_for_school,           
            org_number= org_number,  
        )
        return Response({"status": "success", **result})
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Failed to fetch users for org {org_number}: {str(e)}"
        }, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def import_groups_and_users_api(request, org_number):
    """
    Import groups and users for a specific school from previously fetched files.
    """
    try:
        school = models.School.objects.filter(org_number=org_number).first()
        target = school.display_name if school else org_number

        is_dryrun_enabled = _get_flag(request.data, 'is_dryrun_enabled', False)
        is_overwrite_enabled = _get_flag(request.data, 'is_overwrite_enabled', False)
        is_crash_on_error_enabled = _get_flag(request.data, 'is_crash_on_error_enabled', False)
        
        result = run_with_task_tracking(
            job_name='import_groups_and_users',
            target_id=target,
            func=import_groups_and_users,
            org_number=org_number,
            is_dryrun_enabled=is_dryrun_enabled,
            is_overwrite_enabled=is_overwrite_enabled,
            is_crash_on_error_enabled=is_crash_on_error_enabled,
        )

        return Response({
            "status": "success",
            "message": f"Import of groups and users completed for school {target}",
            "org_number": org_number,
             **result
        })
    except Exception as e:
        return Response({
            "status": "error",
            "message": f"Import of groups and users failed: {str(e)}",
            "org_number": org_number
        }, status=500)