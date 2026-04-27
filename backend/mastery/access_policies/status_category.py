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
            school_ids_via_user_school = UserSchool.objects.filter(
                user_id=requester.id).values_list(
                "school_id", flat=True)
            school_ids_via_user_group = UserGroup.objects.filter(
                user_id=requester.id).values_list(
                "group__school_id", flat=True)
            school_ids = list(set(school_ids_via_user_school).union(set(school_ids_via_user_group)))
            return qs.filter(school_id__in=school_ids).distinct()
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
