from rest_access_policy import AccessPolicy
from django.contrib.auth.models import AnonymousUser

# Override AccessPolicy for Group model
class CustomAccessPolicy(AccessPolicy):
    group_prefix = "role:"

    def get_user_group_values(self, user) -> list[str]:
        # shorcircuit AnonymouseUser
        if isinstance(user, AnonymousUser):
            return []

        values = []
        if user.is_superadmin:
            values.append("superadmin")
        try:
            # Collect role names from memberships, e.g. 'teacher', 'student'
            values.extend({ug.role.name for ug in user.user_groups.all()})
        except Exception:
            pass
        return values


class GroupAccessPolicy(CustomAccessPolicy):
    """
    Access rules:
    - Superadmin can do anything on any group.
    - Teacher can list their own groups (scoped) and retrieve groups they teach.
    - Others are denied.
    """
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Teacher: can list only groups they teach
        {
            "action": ["list"],
            "principal": ["role:teacher"],
            "effect": "allow",
        },
        # Teacher: can retrieve only groups they teach
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_group_teacher",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        """
        Limit list results:
        - superadmin: everything
        - teacher: only their groups
        - others: empty
        """
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            teacher_groups = user.role_groups("teacher")
            return qs.filter(id__in=teacher_groups.values("id"))
        except Exception:
            return qs.none()


    def is_group_teacher(self, request, view, action, obj=None):
        # When evaluated in has_permission (no object yet), defer to object-level check
        if obj is None:
            return True

        # Resolve the group instance
        group = obj
        try:
            from mastery.models import Group
            if not isinstance(group, Group) and hasattr(view, "get_object"):
                group = view.get_object()
        except Exception:
            return False

        user = request.user
        return bool(user and user.is_authenticated and group.get_teachers().filter(id=user.id).exists())
