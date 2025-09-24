from .base import BaseAccessPolicy
from django.db.models import Q
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
            teacher_groups = user.teacher_groups
            student_groups = user.student_groups
            return qs.filter(
                Q(id__in=teacher_groups.values("id"), is_enabled=True) |
                Q(id__in=student_groups.values("id"), is_enabled=True)
            ).distinct()
        except Exception as error:
            logger.debug("GroupAccessPolicy.scope_queryset error: %s", error)
            return qs.none()

    # True if requester is member of enabled group
    def is_member_of_enabled_group(self, request, view, action):
        try:
            requester = request.user
            target_group = view.get_object()
            return requester.groups.filter(id=target_group.id, is_enabled=True).exists()
        except Exception:
            return False
