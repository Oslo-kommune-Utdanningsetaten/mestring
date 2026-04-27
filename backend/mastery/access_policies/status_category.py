import logging
from django.db.models import Q
from .base import BaseAccessPolicy
from mastery.models import UserGroup, UserSchool

logger = logging.getLogger(__name__)


class StatusCategoryAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Users can list and retrieve statuse categories according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # School admins can CRUD statuses categories belonging to their school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:admin"],
            "effect": "allow",
            "condition": "is_admin_at_school"
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        """
        Filter statuses based on who can see them:
        - Everyone: StatusCategories at their schools can be read
        """
        requester = request.user
        if not requester:
            return qs.none()
        if requester.is_superadmin:
            return qs
        try:
            school_member_ids = UserGroup.objects.filter(
                user_id=requester.id).values_list(
                "school_id", flat=True).distinct()
            school_employee_ids = UserSchool.objects.filter(
                user_id=requester.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            # Anyone with a group membership at the school can see status categories at that school
            if school_member_ids:
                filters |= Q(school_id__in=school_member_ids)

            # School employees: All statuses categories at their schools
            if school_employee_ids:
                filters |= Q(school_id__in=school_employee_ids)

            return qs.filter(filters).distinct()
        except Exception:
            logger.exception("StatusCategoryAccessPolicy.scope_queryset")
            return qs.none()

    # True if requester is admin at the school which owns the status category
    def is_admin_at_school(self, request, view, action):
        try:
            if action == 'create':
                school_id = request.data.get("school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                status_category = view.get_object()
                if not status_category:
                    return False
                school_id = status_category.school_id

            if not school_id:
                return False

            school_admin_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name="admin").values_list("school_id", flat=True).distinct()

            return school_id in school_admin_ids

        except Exception:
            logger.exception("StatusCategoryAccessPolicy.is_admin_at_school")
            return False
