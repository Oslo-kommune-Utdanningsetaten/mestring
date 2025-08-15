from .base import BasicAccessPolicy
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class UserAccessPolicy(BasicAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # List: any authenticated user may list according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Retrieve: authenticated user may retrieve themselves
        {
            "action": ["retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_user_self",
        },
        # Teacher can retrieve users in groups they teach
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_group_teacher",
        },
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            teacher_groups = user.teacher_groups
            student_groups = user.student_groups
            # the incoming queryset is all users, so we filter by groups
            new_qs = qs.filter(
                Q(id=user.id) |  # ensure self always visible
                Q(user_groups__group__in=teacher_groups) |
                Q(user_groups__group__in=student_groups)
            ).distinct()
            return new_qs
        except Exception:
            return qs.none()


    def is_user_self(self, request, view, action, obj=None):
        # For permission phase (obj is None) allow; queryset scoping enforces visibility
        if obj is None:
            return True
        try:
            target_user = obj
            # If requesting themselves, allow access
            return bool(request.user.id == target_user.id)
        except Exception as e:
            return False


    def is_group_teacher(self, request, view, action, obj=None):
        # When evaluated in has_permission (no object yet), defer to object-level check
        if obj is None:
            return True
        try:
            request_user = request.user
            target_user = obj
            # Teacher groups (where requester has role=teacher)
            teacher_group_ids = request_user.teacher_groups.values_list("id", flat=True)
            if not teacher_group_ids:
                return False
            # Does target user belong to any of those groups?
            return target_user.user_groups.filter(group_id__in=teacher_group_ids).exists()
        except Exception as e:
            return False
