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
        if getattr(user, 'is_superadmin', False):
            logger.debug("SubjectAccessPolicy.scope_queryset superadmin user=%s", getattr(user, 'id', None))
            return qs
        try:
            user_schools = user.get_schools()
            logger.debug(
                "SubjectAccessPolicy.scope_queryset user=%s schools=%s",
                getattr(user, 'id', None),
                list(user_schools.values_list('id', flat=True))
            )
            return qs.filter(
                Q(owned_by_school__in=user_schools) |
                Q(group__school__in=user_schools)
            ).distinct()
        except Exception as e:
            logger.debug("SubjectAccessPolicy.scope_queryset user=%s exception=%s", getattr(user, 'id', None), e)
            return qs.none()