from .base import BaseAccessPolicy


class MasterySchemaAccessPolicy(BaseAccessPolicy):
    # Which mastery schemas exist is not a secret
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve all mastery schemas
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    # Scope queryset to all roles
    def scope_queryset(self, request, qs):
        return qs
