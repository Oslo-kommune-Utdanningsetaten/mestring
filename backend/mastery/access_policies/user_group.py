from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import UserSchool, UserGroup
import logging
logger = logging.getLogger(__name__)


class UserGroupAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Logged in users have list and retrieve access according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.is_superadmin:
            return qs
        try:
            school_admin_ids = UserSchool.objects.filter(
                user_id=user.id, role__name__in=["admin", "inspector"]
            ).values_list("school_id", flat=True).distinct()

            return qs.filter(
                Q(group__school_id__in=school_admin_ids) |
                Q(user_id=user.id)
            ).distinct()
        except Exception:
            logger.exception("UserGroupAccessPolicy.scope_queryset")
            return qs.none()
