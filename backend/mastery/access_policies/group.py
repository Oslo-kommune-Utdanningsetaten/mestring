from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import UserSchool, Group
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
        # School admins have full access to groups belonging to their school
        {
            "action": ["*"],
            "principal": ["role:admin"],
            "effect": "allow",
            "condition": "is_admin_at_school",
        },
        # Authenticated user can list according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Teachers and students can retrieve groups they are member of
        {
            "action": ["retrieve"],
            "principal": ["role:student", "role:teacher"],
            "effect": "allow",
            "condition": "is_member_of_enabled_group",
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
                user_id=user.id, role__name="admin").values_list("school_id", flat=True).distinct()
            teacher_groups = user.teacher_groups
            student_groups = user.student_groups
            return qs.filter(
                Q(id__in=teacher_groups.values("id"), is_enabled=True) |
                Q(id__in=student_groups.values("id"), is_enabled=True) |
                Q(school_id__in=school_admin_ids)
            ).distinct()
        except Exception:
            logger.exception("GroupAccessPolicy.scope_queryset error")
            return qs.none()

    # True if requester is admin at the group's school
    def is_admin_at_school(self, request, view, action):
        group_id = self.get_target_id(view)
        if not group_id:
            return False
        # Get the school id cheaply (None if group absent)
        school_id = (
            Group.objects.filter(id=group_id)
            .values_list('school_id', flat=True)
            .first()
        )
        if not school_id:
            return False
        return UserSchool.objects.filter(
            user_id=request.user.id,
            school_id=school_id,
            role__name="admin"
        ).exists()

    # True if requester is member of enabled group
    def is_member_of_enabled_group(self, request, view, action):
        group_id = self.get_target_id(view)
        return bool(group_id) and request.user.groups.filter(id=group_id, is_enabled=True).exists()
