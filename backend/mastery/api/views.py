from .. import models, serializers
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_access_policy import AccessViewSetMixin
from mastery.access_policies import GroupAccessPolicy, SchoolAccessPolicy, SubjectAccessPolicy, UserAccessPolicy, GoalAccessPolicy


def get_request_param(query_params, name: str):
    """
    Return the stripped string value of a query parameter, or None if
    the parameter is missing, empty, or only whitespace.
    """
    value = query_params.get(name)
    if value is None:
        return None
    value = value.strip()
    if value == '':
        return None
    return value

# School


class SchoolViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    filterset_fields = ['is_service_enabled']
    access_policy = SchoolAccessPolicy

    def get_queryset(self):
        return self.access_policy().scope_queryset(self.request, super().get_queryset())


# User
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='Filter users by School ID (users in any group of that school)',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='roles',
                description='Filter users by roles they have. Comma-separated list of role names (e.g., student,teacher)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='groups',
                description='Filter users by group membership. Comma-separated list of group IDs',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class UserViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    access_policy = UserAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())
        if self.action == 'list':
            school_param = get_request_param(
                self.request.query_params, 'school')
            roles_param = get_request_param(self.request.query_params, 'roles')
            groups_param = get_request_param(
                self.request.query_params, 'groups')

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            qs = qs.filter(user_groups__group__school_id=school_param)
            if roles_param:
                role_names = [role.strip()
                              for role in roles_param.split(',') if role]
                if role_names:
                    qs = qs.filter(user_groups__role__name__in=role_names)
            if groups_param:
                group_ids = [group.strip()
                             for group in groups_param.split(',') if group]
                if group_ids:
                    qs = qs.filter(user_groups__group_id__in=group_ids)
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


# Group
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='Filter users by School ID (users in any group of that school)',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='type',
                description='Filter groups by type (e.g., teaching, basis)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class GroupViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    access_policy = GroupAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())
        if self.action == 'list':
            school_param = get_request_param(
                self.request.query_params, 'school')
            type_param = get_request_param(self.request.query_params, 'type')

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            qs = qs.filter(school_id=school_param)
            if type_param:
                qs = qs.filter(type=type_param.lower())
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


# Subject
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='Filter subject by subject.groups belonging to school',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='owned_by',
                description='Filter subject by owned_by_school (school ID)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class SubjectViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    access_policy = SubjectAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())

        if self.action == 'list':
            school_param = get_request_param(
                self.request.query_params, 'school')
            owned_by_school_param = get_request_param(
                self.request.query_params, 'owned_by')

            # Require at least one of the two parameters (school OR owned_by)
            if (not school_param) and (not owned_by_school_param):
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'At least one of "school" or "owned_by" parameters are required.'})

            # Build a union of the selected filters instead of constraining sequentially
            result_qs = qs.none()
            if school_param:
                result_qs = qs.filter(groups__school_id=school_param)
            if owned_by_school_param:
                result_qs = result_qs | qs.filter(
                    owned_by_school_id=owned_by_school_param)

            return result_qs.distinct()
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


# Goal
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='student',
                description='Filter goals by the student owning them. Using this parameter will return both personal goals and group goals where the student is a member.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='subject',
                description='Filter goals by subject',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='group',
                description='Filter goals by group',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class GoalViewSet(AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Goal.objects.all()
    serializer_class = serializers.GoalSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['student_id', 'group_id', 'subject_id']
    ordering_fields = ['created_at', 'updated_at', 'title', 'sort_order']
    ordering = ['sort_order']
    access_policy = GoalAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())

        if self.action == 'list':
            student_param = get_request_param(
                self.request.query_params, 'student')
            subject_param = get_request_param(
                self.request.query_params, 'subject')
            group_param = get_request_param(self.request.query_params, 'group')

            if (not student_param) and (not subject_param) and (not group_param):
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'At least one of "subject", "group" or "student" parameters are required.'})

            if (group_param and subject_param):
                raise ValidationError(
                    {'error': 'wrong-parameter', 'message': 'group and subject parameters cannot be used together (goals are either personal or group).'})

            if student_param:
                qs = qs.filter(
                    Q(student_id=student_param) |
                    Q(group__user_groups__user_id=student_param)
                )
            if group_param:
                qs = qs.filter(group_id=group_param)
            if subject_param:
                qs = qs.filter(subject_id=subject_param)

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


# Role

class RoleViewSet(viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer


# Situation

class SituationViewSet(viewsets.ModelViewSet):
    queryset = models.Situation.objects.all()
    serializer_class = serializers.SituationSerializer


# Observation

class ObservationViewSet(viewsets.ModelViewSet):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    filterset_fields = ['student_id', 'goal_id']


# Status

class StatusViewSet(viewsets.ModelViewSet):
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer


# Mastery

class MasterySchemaViewSet(viewsets.ModelViewSet):
    queryset = models.MasterySchema.objects.all()
    serializer_class = serializers.MasterySchemaSerializer
