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
        group = view.get_object()
        if not group:
            return False
        school_id = self.scope_queryset(
            request, Group.objects.filter(id=group.id)).values_list(
            "school_id", flat=True).first()
        if not school_id:
            return False
        return UserSchool.objects.filter(
            user_id=request.user.id,
            school_id=school_id,
            role__name="admin"
        ).exists()
