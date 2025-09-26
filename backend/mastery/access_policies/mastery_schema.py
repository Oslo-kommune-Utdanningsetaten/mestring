from .base import BaseAccessPolicy
import logging
logger = logging.getLogger(__name__)


class MasterySchemaAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve all mastery schemas for schools they belong to
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    # Scope queryset to all roles
    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            user_schools = user.get_schools()
            return qs.filter(school_id__in=user_schools.values("id"))
        except Exception as error:
            logger.error("MasterySchemaAccessPolicy.scope_queryset error: %s", error)
            return qs.none()
