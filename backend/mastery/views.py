from mastery import models, serializers
from rest_framework import viewsets, status, views, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import JSONParser, FormParser
from rest_framework.filters import OrderingFilter
from django.db import connection
import json
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from mastery.imports.task_tracker import run_with_task_tracking,import_groups_and_users
from mastery.imports.feide_api import fetch_and_store_feide_groups_for_school, fetch_feide_users_for_school
from mastery.imports.school_importer import import_school_from_feide


# More about filtering in Django REST Framework:
# https://www.django-rest-framework.org/api-guide/filtering/

class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    filterset_fields = ['is_service_enabled']

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='roles',
                description='Comma-separated list of role names to filter users by (e.g., student,teacher)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
    @action(
        detail=True,
        methods=['get'],
        url_path='users',
        description="Get all users belonging to groups in this school, optionally filtered by role",
        serializer_class=serializers.UserSerializer
    )
    def users(self, request, pk=None):
        """Get all users from groups belonging to this school"""
        school = self.get_object()
        
        # Get users from groups belonging to this school
        users_qs = models.User.objects.filter(
            user_groups__group__school=school
        ).distinct()
        
        # Apply role filtering if provided
        roles_param = request.query_params.get('roles')
        if roles_param:
            role_names = [r.strip() for r in roles_param.split(',') if r.strip()]
            users_qs = users_qs.filter(user_groups__role__name__in=role_names)
        
        serializer = self.get_serializer(users_qs, many=True, context={'request': request})
        return Response(serializer.data)
    

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    filterset_fields = ['maintened_by_school']


class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='roles',
                description='Comma-separated list of role names to filter groups by',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
    @action(
        detail=True,
        methods=['get'],
        url_path='groups',
        description="List all groups for this user, optional ?roles=role1,role2 filter",
        serializer_class=serializers.GroupSerializer
    )
    def groups(self, request, pk=None):
        user = self.get_object()
        qs = models.Group.objects.filter(user_groups__user=user)
        roles_param = request.query_params.get('roles')

        if roles_param:
            role_names = [r.strip() for r in roles_param.split(',') if r.strip()]
            qs = qs.filter(user_groups__role__name__in=role_names)

        qs = qs.distinct()
        # this will use the GroupSerializer defined above
        serializer = self.get_serializer(qs, many=True, context={'request': request})
        return Response(serializer.data)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='subjectId',
                description='Filter goals by subject ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='groupId',
                description='Filter goals by group ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
    @action(
        detail=True,
        methods=['get'],
        url_path='goals',
        description="List all goals for this user (both personal and group goals)",
        serializer_class=serializers.GoalSerializer
    )
    def goals(self, request, pk=None):
        """Get all goals for a student - both personal goals and group goals"""
        user = self.get_object()
        
        # Get personal goals where student is directly assigned
        personal_goals = models.Goal.objects.filter(student=user)
        
        # Get group goals from all groups the user belongs to as a student
        student_groups = user.role_groups('student')
        group_goals = models.Goal.objects.filter(group__in=student_groups)
        
        # Combine both querysets
        all_goals = personal_goals.union(group_goals).order_by('created_at')
        
        # Apply filters based on query parameters
        subject_id = request.query_params.get('subjectId')
        group_id = request.query_params.get('groupId')
        
        if subject_id:
            all_goals = all_goals.filter(subject_id=subject_id)
        
        if group_id:
            all_goals = all_goals.filter(group_id=group_id)
        
        serializer = self.get_serializer(all_goals, many=True, context={'request': request})
        return Response(serializer.data)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filterset_fields = ['school', 'type']
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Retrieve all members of a group"""
        group = self.get_object()
        group_members = models.UserGroup.objects.filter(group=group)
        serializer = serializers.NestedGroupUserSerializer(group_members, many=True)
        return Response(serializer.data)


class GoalViewSet(viewsets.ModelViewSet):
    queryset = models.Goal.objects.all()
    serializer_class = serializers.GoalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['student_id', 'group_id', 'subject_id']
    ordering_fields = ['created_at', 'updated_at', 'title', 'sort_order']
    ordering = ['sort_order']  # Default ordering


class SituationViewSet(viewsets.ModelViewSet):
    queryset = models.Situation.objects.all()
    serializer_class = serializers.SituationSerializer


class ObservationViewSet(viewsets.ModelViewSet):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    filterset_fields = ['student_id', 'goal_id']

class StatusViewSet(viewsets.ModelViewSet):
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer


class UserGroupViewSet(viewsets.ModelViewSet):
    queryset = models.UserGroup.objects.all()
    serializer_class = serializers.UserGroupSerializer


class MasterySchemaViewSet(viewsets.ModelViewSet):
    queryset = models.MasterySchema.objects.all()
    serializer_class = serializers.MasterySchemaSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    """Simple ping endpoint to check API and database availability"""
    db_status = 'unknown'
    status = 200
    # Lightweight database check - just run a simple query
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = 'up'
    except Exception:
        db_status = 'down'
        status = 503
    
    return Response(data={
        "api": "up",
        "db": db_status
    }, status=status)


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
