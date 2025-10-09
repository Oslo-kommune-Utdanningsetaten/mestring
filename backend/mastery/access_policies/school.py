from .base import BaseAccessPolicy
import logging
logger = logging.getLogger(__name__)


class SchoolAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve schools they belong to
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            user_schools = user.get_schools()
            return qs.filter(id__in=user_schools.values("id"))
        except Exception:
            logger.exception("SchoolAccessPolicy.scope_queryset error")
            return qs.none()
