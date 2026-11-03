from .base import BaseAccessPolicy
from mastery.models import UserSchool, UserGroup
import logging

logger = logging.getLogger(__name__)


class TagCollectionAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # School admins and inspectorshave full access to tag_collections belonging to their school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:admin", "role:inspector"],
            "effect": "allow",
            "condition": "is_admin_or_inspector_at_school",
        },
        # Users with the teacher role in a user_group, attached to a group witht the subject in question, can CRUD tags the tag_collections for that subject and school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_teacher_in_user_group_for_subject",
        },
        # Authenticated users can list tag_collections according to scope_queryset (via school and group membership)
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
            # TagCollections attached to a school where the user belongs
            return qs.filter(school_id__in=school_ids).distinct()
        except Exception:
            logger.exception("TagCollectionAccessPolicy.scope_queryset")
            return qs.none()

    # True if requester is admin or inspector at the school which owns the tag_collection
    def is_admin_or_inspector_at_school(self, request, view, action):
        try:
            if action == 'create':
                school_id = request.data.get("school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                tag_collection = view.get_object()
                if not tag_collection.school_id:
                    return False
                school_id = tag_collection.school_id
            else:
                return False

            if not school_id:
                return False

            school_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            return school_id in school_ids

        except Exception:
            logger.exception("TagCollectionAccessPolicy.is_admin_or_inspector_at_school")
            return False

    # True if requester is a teacher in a user_group attached to a group with the subject in question
    def is_teacher_in_user_group_for_subject(self, request, view, action):
        try:
            if action == 'create':
                subject_id = request.data.get("subject_id")
                school_id = request.data.get("school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                tag_collection = view.get_object()
                if not tag_collection.subject_id:
                    return False
                subject_id = tag_collection.subject_id
                school_id = tag_collection.school_id
            else:
                return False

            if not subject_id or not school_id:
                return False

            group_ids = UserGroup.objects.filter(
                user_id=request.user.id, role__name="teacher", group__subject_id=subject_id,
                group__school_id=school_id,).values_list(
                "group_id", flat=True).distinct()

            return bool(group_ids)

        except Exception:
            logger.exception("TagCollectionAccessPolicy.is_teacher_in_user_group_for_subject")
            return False
