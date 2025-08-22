from rest_access_policy import AccessPolicy
from django.contrib.auth.models import AnonymousUser

class BaseAccessPolicy(AccessPolicy):
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
