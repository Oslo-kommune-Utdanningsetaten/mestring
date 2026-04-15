from .. import models, serializers
from django.db.models import Q, Prefetch, Exists, OuterRef
from datetime import datetime
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_access_policy import AccessViewSetMixin
from mastery.access_policies import GroupAccessPolicy, SchoolAccessPolicy, SubjectAccessPolicy, UserAccessPolicy, GoalAccessPolicy, RoleAccessPolicy, MasterySchemaAccessPolicy, ObservationAccessPolicy, UserSchoolAccessPolicy, UserGroupAccessPolicy, DataMaintenanceTaskAccessPolicy, SituationAccessPolicy, StatusAccessPolicy
from .api_functions import get_request_param
import logging

logger = logging.getLogger(__name__)


def apply_deleted_filter(query_params, qs):
    deleted_param, _ = get_request_param(query_params, 'deleted')
    if deleted_param == 'only':
        # Only deleted items
        return qs.filter(deleted_at__isnull=False)
    elif deleted_param == 'include':
        # All items, deleted and non-deleted
        return qs
    # Default: non-deleted
    return qs.filter(deleted_at__isnull=True)


def apply_valid_group_filter(query_params, qs):
    is_valid_param, is_valid_set = get_request_param(query_params, 'is_valid')

    if is_valid_set and not is_valid_param:
        # Only invalid groups
        return qs.outside_validity_period()
    else:
        # By default, include only valid groups
        return qs.within_validity_period()


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
                name='ids',
                description='Only return users with these IDs (comma-separated list of user ids)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='roles',
                description='Filter users by roles the users have. Comma-separated list of role names (student, teacher, staff, admin, inspector)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='teacher',
                description='Filter users by what kind of groups the teach. Implies roles=teacher. Value should be either "basis" or "teaching".',
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
            OpenApiParameter(
                name='deleted',
                description='Filter users by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
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

        qs = apply_deleted_filter(self.request.query_params, qs)

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            ids_param, _ = get_request_param(self.request.query_params, 'ids')
            roles_param, _ = get_request_param(self.request.query_params, 'roles')
            groups_param, _ = get_request_param(self.request.query_params, 'groups')
            teacher_param, _ = get_request_param(self.request.query_params, 'teacher')
            include_superadmins = False

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            # Build filters additively based on provided parameters
            # Start with base filters for both possible paths (user_groups and user_schools)
            user_group_filters = Q(
                user_groups__group__school_id=school_param,
                user_groups__deleted_at__isnull=True
            )
            user_school_filters = Q(user_schools__school_id=school_param)

            # Add group filter if specified (only applies to user_groups path)
            if groups_param:
                group_ids = [group.strip() for group in groups_param.split(',') if group]
                if group_ids:
                    user_group_filters &= Q(user_groups__group_id__in=group_ids)

            # Add role filter if specified (applies to both paths)
            if roles_param:
                role_names = [role.strip() for role in roles_param.split(',') if role]
                if role_names:
                    user_group_filters &= Q(user_groups__role__name__in=role_names)
                    user_school_filters &= Q(user_schools__role__name__in=role_names)
                    include_superadmins = 'superadmin' in role_names

            # Add filter for what kind of teacher the user is
            if teacher_param:
                user_group_filters &= Q(user_groups__group__type=teacher_param,
                                        user_groups__role__name__in=['teacher'])

            # Add user id filter if specified
            if ids_param:
                user_ids = [user_id.strip() for user_id in ids_param.split(',') if user_id]
                if user_ids:
                    qs = qs.filter(id__in=user_ids)

            # Apply filters: if groups specified, only via user_groups; otherwise both paths
            if groups_param:
                # Groups param restricts to only the user_groups path
                qs = qs.filter(user_group_filters)
            else:
                # No groups: users can match via either user_groups OR user_schools
                qs = qs.filter(user_group_filters | user_school_filters)

            # If filtering by roles and superadmin is included, also include superadmins who may not have a UserSchool or UserGroup entry
            if include_superadmins:
                qs = qs | self.access_policy().scope_queryset(self.request, super().get_queryset()).filter(is_superadmin=True)
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
                description='Role name (e.g., student, teacher, staff, admin, inspector)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='deleted',
                description='Filter user_schools by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
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
        qs = apply_deleted_filter(self.request.query_params, qs)

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
                description='Role name (e.g., student, teacher, staff, admin, inspector)',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='deleted',
                description='Filter user_goups by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
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
        qs = apply_deleted_filter(self.request.query_params, qs)

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
                description='Filter groups by School ID (groups at school)',
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
                name='subject',
                description='Filter groups by the subject their subject',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='enabled',
                description='Filter groups by whether they are enabled for use: "only" (default, only enabled), "include" (both enabled and disabled), or "exclude" (only disabled)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='deleted',
                description='Filter groups by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='is_valid',
                description='Filter groups by whether they are valid by date',
                required=False,
                type={'type': 'boolean'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class GroupViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    access_policy = GroupAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('display_name')
        qs = apply_deleted_filter(self.request.query_params, qs)
        qs = apply_valid_group_filter(self.request.query_params, qs)

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            type_param, _ = get_request_param(self.request.query_params, 'type')
            user_param, _ = get_request_param(self.request.query_params, 'user')
            subject_param, _ = get_request_param(self.request.query_params, 'subject')
            roles_param, _ = get_request_param(self.request.query_params, 'roles')
            ids_param, _ = get_request_param(self.request.query_params, 'ids')
            enabled_param, _ = get_request_param(self.request.query_params, 'enabled')

            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            if roles_param and not user_param:
                logger.warning(
                    'The "roles" parameter was provided without the "user" parameter. This is probably a unintended.')

            # Apply school filter
            qs = qs.filter(school_id=school_param)

            # Apply type filter if specified
            if type_param:
                qs = qs.filter(type=type_param.lower())

            # Build user_groups filters additively if user or roles are specified
            if user_param or roles_param:
                user_groups_filters = Q(user_groups__deleted_at__isnull=True)

                if user_param:
                    user_groups_filters &= Q(user_groups__user_id=user_param)

                if roles_param:
                    role_names = [role.strip() for role in roles_param.split(',') if role]
                    if role_names:
                        user_groups_filters &= Q(user_groups__role__name__in=role_names)

                qs = qs.filter(user_groups_filters)

            # Apply subject filter if specified
            if subject_param:
                qs = qs.filter(subject_id=subject_param)

            # Apply ids filter if specified
            if ids_param:
                ids = [id.strip() for id in ids_param.split(',') if id]
                if ids:
                    qs = qs.filter(id__in=ids)

            # Apply enabled filter
            if enabled_param:
                if enabled_param == 'exclude':
                    qs = qs.filter(is_enabled=False)  # Only disabled groups
                elif enabled_param == 'only':
                    qs = qs.filter(is_enabled=True)  # Only enabled groups
                elif enabled_param == 'include':
                    qs = qs  # All groups, deleted and non-deleted
                else:
                    logger.warning("Unknown value for 'enabled' parameter: %s", enabled_param)
            else:
                qs = qs.filter(is_enabled=True)  # default
            return qs

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs.distinct()


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='school',
                description='All subjects belonging to school, either directly via owned_by_school or via groups belonging to school',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='students',
                description='Filter subjects by student participation. Comma-separated list of user IDs',
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
            ),
            OpenApiParameter(
                name='deleted',
                description='Filter subjects by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class SubjectViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer
    access_policy = SubjectAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('display_name')
        qs = apply_deleted_filter(self.request.query_params, qs)

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            student_ids_param, _ = get_request_param(self.request.query_params, 'students')

            is_owned_by_school_param, is_owned_set = get_request_param(
                self.request.query_params, 'is_owned_by_school')

            # Require school
            if not school_param:
                raise ValidationError(
                    {'error': 'missing-parameter', 'message': 'The "school" query parameter is required.'})

            qs = qs.filter(
                Q(owned_by_school_id=school_param) |
                Exists(models.Group.objects.filter(subject_id=OuterRef('pk'), school_id=school_param)) |
                Exists(models.Goal.objects.filter(subject_id=OuterRef('pk'), school_id=school_param))
            )

            if student_ids_param:
                student_ids = [student_id.strip()
                               for student_id in student_ids_param.split(',') if student_id]
                if student_ids:
                    qs = qs.filter(
                        # when querying by student_ids, include only subjects where the groups are enabled
                        Exists(
                            models.UserGroup.objects.filter(
                                group__subject_id=OuterRef('pk'),
                                user_id__in=student_ids,
                                deleted_at__isnull=True,
                                group__is_enabled=True
                            )
                        ) |
                        Exists(
                            models.Goal.objects.filter(
                                subject_id=OuterRef('pk'),
                                student_id__in=student_ids
                            )
                        )
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
                name='school',
                description='Filter goals by school',
                required=True,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='student',
                description='Filter goals by the student owning them. Using this parameter will return both individual goals and group goals where the student is a member.',
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
            OpenApiParameter(
                name='deleted',
                description='Filter goals by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='include_observations',
                description='Include related observations in the response',
                required=False,
                type={'type': 'boolean'},
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
        qs = apply_deleted_filter(self.request.query_params, qs)

        if self.action == 'list':
            school_param, _ = get_request_param(self.request.query_params, 'school')
            group_param, _ = get_request_param(self.request.query_params, 'group')
            student_param, _ = get_request_param(self.request.query_params, 'student')
            subject_param, _ = get_request_param(self.request.query_params, 'subject')
            include_observations_param, _ = get_request_param(
                self.request.query_params, 'include_observations')

            if (not school_param) and (not student_param) and (not subject_param) and (not group_param):
                raise ValidationError(
                    {'error': 'missing-parameter',
                     'message': 'At least one of "school", "subject", "group" or "student" parameters are required.'})

            if (group_param and subject_param):
                raise ValidationError(
                    {'error': 'wrong-parameter',
                     'message':
                     'group and subject parameters cannot be used together (goals are either individual or group).'})

            qs = qs.filter(school_id=school_param)

            if group_param:
                qs = qs.filter(group_id=group_param)
            if student_param:
                # Student can be either the owner of a individual goal or a member of a group goal
                qs = qs.filter(
                    Q(student_id=student_param) |
                    Q(group__user_groups__user_id=student_param, group__user_groups__deleted_at__isnull=True)
                )
            if subject_param:
                # Subject can be either on a individual goal or a group goal
                qs = qs.filter(
                    Q(subject_id=subject_param) |
                    Q(group__subject_id=subject_param)
                )
            if include_observations_param and (student_param or group_param):
                # Prefetch observations with access-policy scoping applied
                self.serializer_class = serializers.GoalWithObservationsSerializer
                from mastery.access_policies.observation import ObservationAccessPolicy
                observation_policy = ObservationAccessPolicy()
                observation_qs = observation_policy.scope_queryset(
                    self.request, models.Observation.objects.all())
                # Filter by student or group
                if student_param:
                    observation_qs = observation_qs.filter(student_id=student_param)
                if group_param:
                    observation_qs = observation_qs.filter(goal__group_id=group_param)
                qs = qs.prefetch_related(
                    Prefetch('observations', queryset=observation_qs, to_attr='prefetched_observations')
                )
                return qs
        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='deleted',
                description='Filter roles by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class RoleViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Role.objects.all()
    serializer_class = serializers.RoleSerializer
    access_policy = RoleAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('name')
        qs = apply_deleted_filter(self.request.query_params, qs)
        return qs


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
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset()).order_by('title')
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
                name='group',
                description='Filter observations by students who are member of this group. Basis groups will return observations accross subjects. Teaching groups will return observations for the subject of the group.',
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
            OpenApiParameter(
                name='from',
                description='Filter observations by when they were created, using ISO format date string. E.g. 2025-12-24 will return observations created on or after December 24st, 2025.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='to',
                description='Filter observations by when they were created, using ISO format date string. E.g. 2025-12-24 will return observations created on or before December 24st, 2025.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='school',
                description='Filter observations by goal.school_id',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='deleted',
                description='Filter observations by soft-deleted status: "exclude" (default, only non-deleted), "include" (both deleted and non-deleted), or "only" (only deleted)',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
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
        qs = apply_deleted_filter(self.request.query_params, qs)

        if self.action == 'list':
            student_param, _ = get_request_param(self.request.query_params, 'student')
            observer_param, _ = get_request_param(self.request.query_params, 'observer')
            goal_param, _ = get_request_param(self.request.query_params, 'goal')
            group_param, _ = get_request_param(self.request.query_params, 'group')
            school_param, _ = get_request_param(self.request.query_params, 'school')
            from_param, _ = get_request_param(self.request.query_params, 'from')
            to_param, _ = get_request_param(self.request.query_params, 'to')

            if (not student_param) and (not observer_param) and (not goal_param) and (not group_param) and (not school_param):
                raise ValidationError(
                    {'error': 'missing-parameter',
                     'message': 'At least one of "student", "observer", "group" or "goal" parameters are required.'})

            if student_param:
                qs = qs.filter(
                    Q(student_id=student_param)
                )
            if observer_param:
                qs = qs.filter(observer_id=observer_param)
            if goal_param:
                qs = qs.filter(goal_id=goal_param)
            if school_param:
                qs = qs.filter(goal__school_id=school_param)
            if group_param:
                group = models.Group.objects.filter(
                    id=group_param, deleted_at__isnull=True, is_enabled=True).first()
                if group and group.type == 'basis':
                    # For basis groups, include observations for student members of the group
                    user_groups = models.UserGroup.objects.filter(
                        group_id=group_param,
                        group__is_enabled=True,
                        group__deleted_at__isnull=True,
                        role__name='student',
                        deleted_at__isnull=True
                    )
                    qs = qs.filter(
                        Q(student_id__in=user_groups.values_list('user_id', flat=True))
                    )
                elif group and group.type == 'teaching':
                    # For teaching group, include observations which belong to the groups subject (either via goal->group or directly on the goal)
                    qs = qs.filter(
                        Q(goal__group__id=group_param) |
                        Q(goal__subject_id=group.subject_id)
                    )
            if from_param:
                try:
                    from_date = datetime.fromisoformat(from_param).date()
                except ValueError:
                    raise ValidationError(
                        {'error': 'invalid-parameter',
                         'message': 'Invalid date format for "from" parameter. Use ISO format (YYYY-MM-DD).'})
                qs = qs.filter(observed_at__date__gte=from_date)
            if to_param:
                try:
                    to_date = datetime.fromisoformat(to_param).date()
                except ValueError:
                    raise ValidationError(
                        {'error': 'invalid-parameter',
                         'message': 'Invalid date format for "to" parameter. Use ISO format (YYYY-MM-DD).'})
                qs = qs.filter(observed_at__date__lte=to_date)
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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                name='students',
                description='Filter statuses by students.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='subject',
                description='Filter statuses by subject.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='school',
                description='Filter statuses by school.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='group',
                description='Filter statuses by group.',
                required=False,
                type={'type': 'string', 'enum': ['exclude', 'include', 'only']},
                location=OpenApiParameter.QUERY
            ),
            OpenApiParameter(
                name='editor',
                description='Filter statuses by users who have created or updated it.',
                required=False,
                type={'type': 'string'},
                location=OpenApiParameter.QUERY
            ),
        ]
    )
)
class StatusViewSet(FingerprintViewSetMixin, AccessViewSetMixin, viewsets.ModelViewSet):
    queryset = models.Status.objects.all()
    serializer_class = serializers.StatusSerializer
    access_policy = StatusAccessPolicy

    def get_queryset(self):
        qs = self.access_policy().scope_queryset(self.request, super().get_queryset())
        qs = apply_deleted_filter(self.request.query_params, qs)

        if self.action == 'list':
            students_param, _ = get_request_param(self.request.query_params, 'students')
            school_param, _ = get_request_param(self.request.query_params, 'school')
            subject_param, _ = get_request_param(self.request.query_params, 'subject')
            group_param, _ = get_request_param(self.request.query_params, 'group')
            editor_param, _ = get_request_param(self.request.query_params, 'editor')

            if not school_param:
                raise ValidationError({'error': 'missing-parameter',
                                      'message': 'The "school" parameter is required.'})

            qs = qs.filter(school_id=school_param)

            if students_param:
                student_ids = [student_id.strip() for student_id in students_param.split(',') if student_id]
                if student_ids:
                    qs = qs.filter(student_id__in=student_ids)

            if group_param:
                student_ids = UserGroup.objects.filter(
                    group_id=group_param, role__name='student', deleted_at__isnull=True).values_list(
                    'user_id', flat=True)
                if student_ids:
                    qs = qs.filter(student_id__in=student_ids)

            if subject_param:
                qs = qs.filter(subject_id=subject_param)

            if editor_param:
                qs = qs.filter(Q(created_by_id=editor_param) | Q(updated_by_id=editor_param))

        # non-list actions (retrieve, create, update, destroy) do not require parameters
        return qs
