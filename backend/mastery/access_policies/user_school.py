from .base import BaseAccessPolicy
from mastery.models import UserSchool
import logging
logger = logging.getLogger(__name__)


class UserSchoolAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Users user-school access is determined by scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Users can retrieve their own user-school data
        {
            "action": ["retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_user_owner",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if not user:
            return qs.none()
        if user.is_superadmin:
            return qs
        if user.is_authenticated:
            return qs.filter(user_id=user.id)
        return qs.none()

    def is_user_owner(self, request, view, action):
        try:
            user_school_id = self.get_target_id(view)
            if not user_school_id:
                return False
            qs = self.scope_queryset(request, UserSchool.objects)
            return qs.filter(id=user_school_id).exists()
        except Exception:
            logger.exception("UserSchoolAccessPolicy.is_user_target")
            return False
