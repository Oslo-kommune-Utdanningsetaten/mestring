from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import User

class UserAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated user can list according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Retrieve: authenticated user may retrieve themselves
        {
            "action": ["retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_user_self",
        },
        # Teachers and students can retrieve users in groups they are member of, or teachers at their school
        {
            "action": ["retrieve"],
            "principal": ["role:student", "role:teacher"],
            "effect": "allow",
            "condition_expression": ["(is_in_same_group or is_target_teacher_at_my_school)"],
        },
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if user.is_superadmin:
            return qs
        try:
            groups_where_current_user_is_teacher = user.teacher_groups
            groups_where_current_user_is_student = user.student_groups
            # Collect all teacher user IDs from schools the user is affiliated with
            teacher_ids = User.objects.filter(
                user_groups__group__school__in=user.get_schools(),
                user_groups__role__name='teacher'
            ).values_list('id', flat=True)

            new_qs = qs.filter(
                Q(id=user.id) |  # always include self
                Q(user_groups__group__in=groups_where_current_user_is_teacher) |
                Q(user_groups__group__in=groups_where_current_user_is_student) |
                Q(id__in=teacher_ids)
            ).distinct()
            return new_qs
        except Exception:
            return qs.none()


    # True if requester is the target user  
    def is_user_self(self, request, view, action):
        try:
            target_user = view.get_object()
            return bool(request.user.id == target_user.id)
        except Exception:
            return False


    # True if requester and target share any group (any role)
    def is_in_same_group(self, request, view, action):
        try:
            requester = request.user
            target_user = view.get_object()
            return target_user.user_groups.filter(
                group_id__in=requester.groups.values_list("id", flat=True)
            ).exists()
        except Exception:
            return False


    # True if target user is a teacher at any school the requester belongs to
    def is_target_teacher_at_my_school(self, request, view, action):
        try:
            requester = request.user
            target_user = view.get_object()
            school_ids = list(requester.get_schools().values_list("id", flat=True))
            if not school_ids:
                return False
            # Check if target has a teacher membership in any of these schools
            return target_user.user_groups.filter(
                role__name='teacher',
                group__school_id__in=school_ids
            ).exists()
        except Exception:
            return False