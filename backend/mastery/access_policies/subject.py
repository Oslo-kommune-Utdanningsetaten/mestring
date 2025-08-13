from .base import BasicAccessPolicy

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
            subject_ids = set()
            for school in user.get_schools():
                subject_ids.update(school.get_all_subjects().values_list('id', flat=True))
            return qs.filter(id__in=subject_ids)
        except Exception:
            return qs.none()