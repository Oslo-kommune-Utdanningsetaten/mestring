from .. import models, serializers
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter
from mastery.access_policies.group import GroupAccessPolicy

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
    @action(detail=True, methods=['get'], url_path='users',
            description="Get all users belonging to groups in this school, optionally filtered by role",
            serializer_class=serializers.UserSerializer)
    def users(self, request, pk=None):
        school = self.get_object()
        users_qs = models.User.objects.filter(user_groups__group__school=school).distinct()
        roles_param = request.query_params.get('roles')
        if roles_param:
            role_names = [r.strip() for r in roles_param.split(',') if r.strip()]
            users_qs = users_qs.filter(user_groups__role__name__in=role_names)
        serializer = self.get_serializer(users_qs, many=True, context={'request': request})
        return Response(serializer.data)

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    filterset_fields = ['used_by_school']

class UserViewSet(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(name='roles', description='Comma-separated list of role names to filter groups by',
                             required=False, type={'type': 'string'}, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='school', description='School ID to filter groups by',
                             required=False, type={'type': 'string'}, location=OpenApiParameter.QUERY)
        ]
    )
    @action(detail=True, methods=['get'], url_path='groups',
            description="List all groups for this user, optional ?roles=role1,role2 and ?school=id filters",
            serializer_class=serializers.GroupSerializer)
    def groups(self, request, pk=None):
        user = self.get_object()
        qs = models.Group.objects.filter(user_groups__user=user)
        roles_param = request.query_params.get('roles')
        school_param = request.query_params.get('school')
        if roles_param:
            role_names = [r.strip() for r in roles_param.split(',') if r.strip()]
            qs = qs.filter(user_groups__role__name__in=role_names)
        if school_param:
            qs = qs.filter(school_id=school_param.strip())
        serializer = self.get_serializer(qs.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(name='subjectId', description='Filter goals by subject ID',
                             required=False, type={'type': 'string'}, location=OpenApiParameter.QUERY),
            OpenApiParameter(name='groupId', description='Filter goals by group ID',
                             required=False, type={'type': 'string'}, location=OpenApiParameter.QUERY)
        ]
    )
    @action(detail=True, methods=['get'], url_path='goals',
            description="List all goals for this user (both personal and group goals)",
            serializer_class=serializers.GoalSerializer)
    def goals(self, request, pk=None):
        user = self.get_object()
        personal_goals = models.Goal.objects.filter(student=user)
        student_groups = user.role_groups('student')
        group_goals = models.Goal.objects.filter(group__in=student_groups)
        all_goals = personal_goals.union(group_goals).order_by('created_at')
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
    permission_classes = [GroupAccessPolicy]

    def get_queryset(self):
        return GroupAccessPolicy().scope_queryset(self.request, super().get_queryset())

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        group = self.get_object()
        gm = models.UserGroup.objects.filter(group=group)
        serializer = serializers.NestedGroupUserSerializer(gm, many=True)
        return Response(serializer.data)

class GoalViewSet(viewsets.ModelViewSet):
    queryset = models.Goal.objects.all()
    serializer_class = serializers.GoalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['student_id', 'group_id', 'subject_id']
    ordering_fields = ['created_at', 'updated_at', 'title', 'sort_order']
    ordering = ['sort_order']

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
