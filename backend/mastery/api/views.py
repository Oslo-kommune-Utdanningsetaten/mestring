from .. import models, serializers
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_access_policy import AccessViewSetMixin
from mastery.access_policies import GroupAccessPolicy, SchoolAccessPolicy, SubjectAccessPolicy, UserAccessPolicy, GoalAccessPolicy, RoleAccessPolicy, MasterySchemaAccessPolicy, ObservationAccessPolicy, UserSchoolAccessPolicy, UserGroupAccessPolicy, DataMaintenanceTaskAccessPolicy, SituationAccessPolicy, StatusAccessPolicy


def get_request_param(query_params, name: str):
    """
    Return a tuple:
    The python value of a query parameter, or None if the parameter is missing, empty, or only whitespace.
    A boolean indicating whether the parameter was present in the query parameters.
    """
    is_key_present = name in query_params
    value = query_params.get(name)
    if value is None:
        return None, is_key_present
    value = value.strip()
    if value == '':
        return None, is_key_present
    if value.lower() == 'false':
        return False, is_key_present
    if value.lower() == 'true':
        return True, is_key_present
    return value, is_key_present


class FingerprintViewSetMixin:

    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = getattr(serializer, "instance", None)
        instance.created_by = self.request.user
        instance.updated_by = self.request.user
        instance.save(update_fields=["created_by", "updated_by"])

    def perform_update(self, serializer):
        super().perform_update(serializer)
        instance = getattr(serializer, "instance", None)
        instance.updated_by = self.request.user
        instance.save(update_fields=["updated_by"])


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='is_service_enabled',
                description='Filter schools by whether the mastery service is enabled',
                required=False,
                type={'type': 'boolean'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class SchoolViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    filterset_fields = ['is_service_enabled']
    access_policy = SchoolAccessPolicy

    def get_queryset(self):
        return self.access_policy().scope_queryset(self.request, super().get_queryset())


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
                description='Filter users by roles the users have. Comma-separated list of role names (e.g., student,teacher)',
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
class UserViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    access_policy = UserAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('name')
        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            roles_param, _ = get_request_param(self.request.query_params, 'roles')
            groups_param, _ = get_request_param(self.request.query_params, 'groups')

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            # Filter by school: include users in groups OR users directly affiliated via UserSchool
            qs = qs.filter(
                Q(user_groups__group__school_id=school_param) |
                Q(user_schools__school_id=school_param)
            )
            if roles_param:
                role_names = [role.strip() for role in roles_param.split(',') if role]
                if role_names:
                    qs = qs.filter(
                        Q(user_groups__role__name__in=role_names) |
                        Q(user_schools__role__name__in=role_names)
                    )
            if groups_param:
                group_ids = [group.strip() for group in groups_param.split(',') if group]
                if group_ids:
                    qs = qs.filter(user_groups__group_id__in=group_ids)
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='School ID',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='user',
                description='User ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='role',
                description='Role name (e.g., student, teacher, staff, admin)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class UserSchoolViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.UserSchool.objects.all()
    serializer_class = serializers.NestedUserSchoolSerializer
    access_policy = UserSchoolAccessPolicy

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return serializers.UserSchoolSerializer
        return serializers.NestedUserSchoolSerializer

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            user_param, _ = get_request_param(self.request.query_params, 'user')
            role_param, _ = get_request_param(self.request.query_params, 'role')

            if not school_param:
                raise ValidationError({'error': 'missing-parameter',
                                      'message': 'The "school" parameter is required.'})

            qs = qs.filter(school_id=school_param)
            if user_param:
                qs = qs.filter(user_id=user_param)
            if role_param:
                qs = qs.filter(role__name=role_param)

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='School ID',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='group',
                description='Group ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='user',
                description='User ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='role',
                description='Role name (e.g., student, teacher, staff, admin)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class UserGroupViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.UserGroup.objects.all()
    serializer_class = serializers.NestedUserGroupSerializer
    access_policy = UserGroupAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            group_param, _ = get_request_param(self.request.query_params, 'group')
            user_param, _ = get_request_param(self.request.query_params, 'user')
            role_param, _ = get_request_param(self.request.query_params, 'role')

            if not school_param:
                raise ValidationError({'error': 'missing-parameter',
                                      'message': 'The "school" parameter is required.'})

            qs = qs.filter(group__school_id=school_param)
            if user_param:
                qs = qs.filter(user_id=user_param)
            if group_param:
                qs = qs.filter(group_id=group_param)
            if role_param:
                qs = qs.filter(role__name=role_param)

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='ids',
                description='Filter by ids (comma-separated list of group ids, e.g., xyx,123)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
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
            OpenApiParameter(
                name='user',
                description='Filter groups by user ID (groups where the user is a member)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='roles',
                description='Filter groups by roles a user has in that group (comma-separated list of role names, e.g., student,teacher)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='is_enabled',
                description='Filter groups by whether they are enabled',
                required=False,
                type={'type': 'boolean'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='subject',
                description='Filter groups by the subject their subject',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class GroupViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    access_policy = GroupAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('display_name')
        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            type_param, _ = get_request_param(self.request.query_params, 'type')
            user_param, _ = get_request_param(self.request.query_params, 'user')
            subject_param, _ = get_request_param(self.request.query_params, 'subject')
            roles_param, _ = get_request_param(self.request.query_params, 'roles')
            ids_param, _ = get_request_param(self.request.query_params, 'ids')
            is_enabled_param, is_enabled_set = get_request_param(self.request.query_params, 'is_enabled')

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            if roles_param and not user_param:
                logger.warning(
                    'The "roles" parameter was provided without the "user" parameter. This is probably a unintended.')

            qs = qs.filter(school_id=school_param)
            if type_param:
                qs = qs.filter(type=type_param.lower())
            if user_param:
                qs = qs.filter(user_groups__user_id=user_param)
            if subject_param:
                qs = qs.filter(subject_id=subject_param)
            if roles_param:
                role_names = [role.strip() for role in roles_param.split(',') if role]
                if role_names:
                    qs = qs.filter(user_groups__role__name__in=role_names)
            if ids_param:
                ids = [id.strip() for id in ids_param.split(',') if id]
                if ids:
                    qs = qs.filter(id__in=ids)
            if is_enabled_set:
                qs = qs.filter(is_enabled=is_enabled_param)
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='All subjects belonging to school, either directly via owned_by_school or via groups belonging to school',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='is_owned_by_school',
                description='Filter subjects on whether they are owned by the given school',
                required=False,
                type={'type': 'boolean'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class SubjectViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    access_policy = SubjectAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('display_name')

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            is_owned_by_school_param, is_owned_set = get_request_param(
                self.request.query_params, 'is_owned_by_school')

            # Require school
            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            qs = qs.filter(
                Q(groups__school_id=school_param) |
                Q(owned_by_school_id=school_param)
            )

            if is_owned_set:
                if is_owned_by_school_param:
                    qs = qs.filter(owned_by_school_id=school_param)
                else:
                    qs = qs.filter(owned_by_school_id=None)
            return qs.distinct()
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


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
class GoalViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Goal.objects.all()
    serializer_class = serializers.GoalSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'updated_at', 'title', 'sort_order']
    ordering = ['sort_order']
    access_policy = GoalAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('sort_order')

        if self.action == 'list':
            group_param, _ = get_request_param(self.request.query_params, 'group')
            student_param, _ = get_request_param(self.request.query_params, 'student')
            subject_param, _ = get_request_param(self.request.query_params, 'subject')

            if (not student_param) and (not subject_param) and (not group_param):
                raise ValidationError(
                    {'error': 'missing-parameter',
                     'message': 'At least one of "subject", "group" or "student" parameters are required.'})

            if (group_param and subject_param):
                raise ValidationError(
                    {'error': 'wrong-parameter',
                     'message':
                     'group and subject parameters cannot be used together (goals are either personal or group).'})

            if group_param:
                qs = qs.filter(group_id=group_param)
            if student_param:
                # Student can be either the owner of a personal goal or a member of a group goal
                qs = qs.filter(
                    Q(student_id=student_param) |
                    Q(group__user_groups__user_id=student_param)
                )
            if subject_param:
                # Subject can be either on a personal goal or a group goal
                qs = qs.filter(
                    Q(subject_id=subject_param) |
                    Q(group__subject_id=subject_param)
                )
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


class RoleViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    access_policy = RoleAccessPolicy

    def get_queryset(self):
        return self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('name')


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='Filter mastery schemas by School ID',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class MasterySchemaViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.MasterySchema.objects.all()
    serializer_class = serializers.MasterySchemaSerializer
    access_policy = MasterySchemaAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('updated_at').desc()
        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            if school_param:
                qs = qs.filter(school_id=school_param)
        return qs


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='student',
                description='Filter observations by the observed student.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='observer',
                description='Filter observations by who has done the observing.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='goal',
                description='Filter observations by goal.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class ObservationViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Observation.objects.all()
    serializer_class = serializers.ObservationSerializer
    access_policy = ObservationAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('observed_at')

        if self.action == 'list':
            student_param, _ = get_request_param(self.request.query_params, 'student')
            observer_param, _ = get_request_param(self.request.query_params, 'observer')
            goal_param, _ = get_request_param(self.request.query_params, 'goal')

            if (not student_param) and (not observer_param) and (not goal_param):
                raise ValidationError(
                    {'error': 'missing-parameter',
                     'message': 'At least one of "student", "observer" or "goal" parameters are required.'})

            if student_param:
                qs = qs.filter(
                    Q(student_id=student_param)
                )
            if observer_param:
                qs = qs.filter(observer_id=observer_param)
            if goal_param:
                qs = qs.filter(goal_id=goal_param)

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='status',
                description='Filter tasks by status',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            )
        ]
    )
)
class DataMaintenanceTaskViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.DataMaintenanceTask.objects.all()
    serializer_class = serializers.DataMaintenanceTaskSerializer
    access_policy = DataMaintenanceTaskAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())

        if self.action == 'list':
            statuts_param, _ = get_request_param(self.request.query_params, 'status')

            if statuts_param:
                qs = qs.filter(statuts=statuts_param)

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


class SituationViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Situation.objects.all()
    serializer_class = serializers.SituationSerializer
    access_policy = SituationAccessPolicy

    def get_queryset(self):
        return self.access_policy().scope_queryset(self.request, super().get_queryset())


class StatusViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer
    access_policy = StatusAccessPolicy

    def get_queryset(self):
        return self.access_policy().scope_queryset(self.request, super().get_queryset())
