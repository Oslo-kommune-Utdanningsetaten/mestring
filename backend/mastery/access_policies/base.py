from rest_access_policy import AccessPolicy
from django.contrib.auth.models import AnonymousUser
from rest_access_policy.access_policy import AnonymousUser as DRFAnonymousUser


class BaseAccessPolicy(AccessPolicy):
    group_prefix = "role:"

    # Return list of strings representing the user's roles
    # Does not include info about where these roles are held (e.g. which school or group)
    def get_user_group_values(self, user) -> list[str]:
        # shorcircuit AnonymousUser
        if isinstance(user, AnonymousUser) or isinstance(user, DRFAnonymousUser):
            return []

        values = []
        if user.is_superadmin:
            values.append("superadmin")
        try:
            # Collect user <--> group affiliations passing through the user_group table (e.g. teacher, student)
            values.extend({ug.role.name for ug in user.user_groups.all()})
            # Collect user <--> school affiliations passing through the user_school table (e.g. school admin)
            values.extend({us.role.name for us in user.user_schools.all()})
        except Exception:
            pass
        return values

    # --- Helper utilities -------------------------------------------------
    def get_target_id(self, view):
        """Return the object lookup value from the URL path.

        Works for custom lookup_url_kwarg or lookup_field (default 'pk'). Returns
        None for list actions or if the kwarg is absent.
        """
        lookup_url_kwarg = getattr(view, 'lookup_url_kwarg', None)
        lookup_field = getattr(view, 'lookup_field', 'pk')
        key = lookup_url_kwarg or lookup_field
        return view.kwargs.get(key)
