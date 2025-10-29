from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import Subject, UserSchool, UserGroup
from rest_framework.exceptions import NotFound
import logging

logger = logging.getLogger(__name__)


class SubjectAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # School admins have full access to subjects belonging to their school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:admin"],
            "effect": "allow",
            "condition": "is_admin_at_school_which_owns_subject",
        },
        # Authenticated users can list subjects according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
    ]

    def scope_queryset(self, request, qs):
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
            return qs.filter(
                # Subjects attached to groups which belong to a school where the user belongs
                Q(groups__school_id__in=school_ids) |
                # Subjects owned by schools where the user belongs
                Q(owned_by_school_id__in=school_ids)
            ).distinct()
        except Exception:
            logger.exception("SubjectAccessPolicy.scope_queryset error")
            return qs.none()

    # True if requester is admin at the school which owns the subject
    def is_admin_at_school_which_owns_subject(self, request, view, action):
        try:
            if action == 'create':
                school_id = request.data.get("owned_by_school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                subject = view.get_object()
                if not subject:
                    return False
                school_id = self.scope_queryset(
                    request, Subject.objects.filter(id=subject.id)).values_list(
                    "owned_by_school_id", flat=True).first()
            if not school_id:
                return False

            school_admin_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name="admin").values_list("school_id", flat=True).distinct()

            return school_id in school_admin_ids

        except Exception:
            logger.exception("SubjectAccessPolicy.belongs_to_group error")
            return False
