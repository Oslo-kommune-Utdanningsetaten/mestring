from .base import BaseAccessPolicy
from mastery.models import UserSchool
import logging
logger = logging.getLogger(__name__)


class MasterySchemaAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # School admins and inspectors can CRUD mastery_schemas belonging to their school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:admin", "role:inspector"],
            "effect": "allow",
            "condition": "is_admin_or_inspector_at_school"
        },
        # Authenticated users can list and retrieve all mastery schemas for schools they belong to
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Everyone else: implicitly denied
    ]

    # Scope queryset to all roles
    def scope_queryset(self, request, qs):
        user = request.user
        if not user:
            return qs.none()
        if user.is_superadmin:
            return qs
        try:
            user_schools = user.get_schools()
            return qs.filter(school_id__in=user_schools.values("id"))
        except Exception:
            logger.exception("MasterySchemaAccessPolicy.scope_queryset")
            return qs.none()

    # True if requester is admin or inspector at the school which owns the mastery_schema
    def is_admin_or_inspector_at_school(self, request, view, action):
        try:
            if action == 'create':
                school_id = request.data.get("school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                mastery_schema = view.get_object()
                if not mastery_schema.school_id:
                    return False
                school_id = mastery_schema.school_id
            else:
                return False

            if not school_id:
                return False

            school_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            return school_id in school_ids

        except Exception:
            logger.exception("MasterySchemaAccessPolicy.is_admin_or_inspector_at_school")
            return False
