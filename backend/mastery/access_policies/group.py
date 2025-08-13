from .base import BasicAccessPolicy
from django.db.models import Q

class GroupAccessPolicy(BasicAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Teacher: can list and retrieve groups they teach
        {
            "action": ["list", "retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_group_teacher",
        },
        # Student: can list and retrieve groups they are students in
        {
            "action": ["list", "retrieve"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_group_student",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            teacher_groups = user.teacher_groups
            student_groups = user.student_groups
            return qs.filter(
                Q(id__in=teacher_groups.values("id")) |
                Q(id__in=student_groups.values("id"))
            ).distinct()
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

    def is_group_student(self, request, view, action, obj=None):
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
        return bool(user and user.is_authenticated and group.get_students().filter(id=user.id).exists())
