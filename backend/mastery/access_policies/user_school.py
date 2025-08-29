from .base import BaseAccessPolicy
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
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        return qs.none()
