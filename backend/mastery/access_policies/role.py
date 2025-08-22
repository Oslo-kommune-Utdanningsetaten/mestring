from .base import BaseAccessPolicy


class RoleAccessPolicy(BaseAccessPolicy):
    # Which roles exist are not secret at all
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve all roles
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
