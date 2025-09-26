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
        except Exception as error:
            logger.error("GroupAccessPolicy.scope_queryset error: %s", error)
            return qs.none()

    # True if requester is admin at the group's school
    def is_admin_at_school(self, request, view, action):
        try:
            target_group = view.get_object()
            # Reuse the queryset logic to check if user is granted access via school admin privileges
            return self.scope_queryset(request, Group.objects).filter(id=target_group.id).exists()
        except Exception:
            return False

    # True if requester is member of enabled group
    def is_member_of_enabled_group(self, request, view, action):
        try:
            requester = request.user
            target_group = view.get_object()
            return requester.groups.filter(id=target_group.id, is_enabled=True).exists()
        except Exception as error:
            logger.error("GroupAccessPolicy.is_member_of_group error", error)
            return False
