from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import UserSchool, Group, UserGroup
import logging
logger = logging.getLogger(__name__)


class GroupAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # School admins can update groups belonging to their school
        {
            "action": ["update", "partial_update"],
            "principal": ["role:admin"],
            "effect": "allow",
            "condition": "is_admin_at_school",
        },
        # Authenticated user can list according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if not user:
            return qs.none()
        if user.is_superadmin:
            return qs
        try:
            school_admin_ids = UserSchool.objects.filter(
                user_id=user.id, role__name__in=["admin", "inspector"]
            ).values_list("school_id", flat=True).distinct()
            teacher_groups = user.teacher_groups
            student_groups = user.student_groups

            # Basis groups where user is a teacher
            basis_teacher_groups = teacher_groups.filter(type='basis')
            # Students in those basis groups
            student_ids_in_basis_groups = UserGroup.objects.filter(
                group__in=basis_teacher_groups,
                role__name='student'
            ).values_list('user_id', flat=True).distinct()
            # Groups those students are members of
            groups_of_basis_students = Group.objects.filter(
                members__id__in=student_ids_in_basis_groups
            ).distinct().values('id')

            return qs.filter(
                Q(id__in=teacher_groups.values("id"), is_enabled=True) |
                Q(id__in=student_groups.values("id"), is_enabled=True) |
                Q(school_id__in=school_admin_ids) |
                Q(id__in=groups_of_basis_students, is_enabled=True)
            ).distinct()
        except Exception:
            logger.exception("GroupAccessPolicy.scope_queryset")
            return qs.none()

    # True if requester is admin at the group's school
    def is_admin_at_school(self, request, view, action):
        group = view.get_object()
        if not group or not group.school_id:
            return False
        return UserSchool.objects.filter(
            user_id=request.user.id,
            school_id=group.school_id,
            role__name="admin"
        ).exists()
