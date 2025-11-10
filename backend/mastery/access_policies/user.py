from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import User, UserSchool, School


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
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        user = request.user
        if not user:
            return qs.none()
        if user.is_superadmin:
            return qs
        try:
            groups_where_current_user_is_teacher = user.teacher_groups
            groups_where_current_user_is_student = user.student_groups

            # All schools where user is admin or inspector
            school_employee_ids = UserSchool.objects.filter(
                user_id=user.id, role__name__in=["admin", "inspector"]
            ).values_list("school_id", flat=True).distinct()

            # All teacher user IDs from schools the user is member of
            teacher_ids = User.objects.filter(
                user_groups__group__school__in=user.get_schools(),
                user_groups__role__name='teacher'
            ).values_list('id', flat=True)

            filters = Q(id=user.id)  # always include self
            filters |= Q(user_groups__group__in=groups_where_current_user_is_teacher)
            filters |= Q(user_groups__group__in=groups_where_current_user_is_student)
            filters |= Q(id__in=teacher_ids)

            # School inspectors and admin: All users (students and teachers) at their schools
            if school_employee_ids:
                # Users with membership in groups at their schools
                filters |= Q(user_groups__group__school_id__in=school_employee_ids)
                # Users employed at their schools
                filters |= Q(user_schools__school_id__in=school_employee_ids)

            return qs.filter(filters).distinct()
        except Exception:
            return qs.none()
