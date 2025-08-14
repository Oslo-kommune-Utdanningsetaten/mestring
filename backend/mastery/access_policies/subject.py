from .base import BasicAccessPolicy
from django.db.models import Q  # added
import logging  # added

logger = logging.getLogger(__name__)  # added

class SubjectAccessPolicy(BasicAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve all subjects for schools they belong to
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
            return qs.filter(
                Q(owned_by_school__in=user_schools) |
                Q(group__school__in=user_schools)
            ).distinct()
        except Exception as e:
            return qs.none()