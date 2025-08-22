from .base import BaseAccessPolicy
from django.db.models import Q
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
        # Authenticated users can list subjects according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Group subjects are available to all users in the group
        {
            "action": ["retrieve"],
            "principal": ["role:student", "role:teacher"],
            "effect": "allow",
            "condition": "belongs_to_group"
        },
        # Personal subjects are available to the creator
        {
            "action": ["retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "is_user_creator"
        },
        # Personal subjects are available to the student
        {
            "action": ["retrieve"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_user_owner"
        },
        # Personal subjects are available to the creator of the attached goal
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_user_creator_of_goal"
        },
        # Teacher may retrieve subjects where a goal's student is in a basis group they teach
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_goal_student_in_basis_group_taught_by_user"
        },
    ]


    def scope_queryset(self, request, qs):
        requester = request.user
        if requester.is_superadmin:
            return qs
        try:
            user_groups_qs = requester.groups.all()
            basis_groups_taught_ids = list(
                requester.teacher_groups.filter(type='basis').values_list('id', flat=True)
            )
            return qs.filter(
                # subjects via any group membership
                Q(groups__in=user_groups_qs) |
                # subjects created by requester
                Q(created_by=requester) |
                # subjects with goals created by requester
                Q(goals__created_by=requester) |
                # subjects with goals for requester as student
                Q(goals__student=requester) |
                # subjects with goals whose student is in a basis group taught by requester
                Q(goals__student__groups__id__in=basis_groups_taught_ids)
            ).distinct()
        except Exception as error:
            logger.debug("SubjectAccessPolicy.scope_queryset error: %s", error)
            return qs.none()


    # True if requester is member of any group that uses this subject
    def belongs_to_group(self, request, view, action):
        try:
            requester = request.user
            subject = view.get_object()
            requester_group_ids = set(requester.groups.values_list("id", flat=True))
            subject_group_ids = set(subject.groups.values_list("id", flat=True))
            return len(requester_group_ids.intersection(subject_group_ids)) > 0
        except Exception as error:
            logger.debug("SubjectAccessPolicy.belongs_to_group error: %s", error)
            return False

    # True if requester created the subject
    def is_user_creator(self, request, view, action):
        try:
            requester = request.user
            subject = view.get_object()
            return subject.created_by == requester
        except Exception as error:
            logger.debug("SubjectAccessPolicy.is_user_creator error: %s", error)
            return False

    # True if requester is 'owner' via being the student of any goal on this subject.
    def is_user_owner(self, request, view, action):
        try:
            requester = request.user
            subject = view.get_object()
            return subject.goals.filter(student=requester).exists()
        except Exception as error:
            logger.debug("SubjectAccessPolicy.is_user_owner error: %s", error)
            return False

    # True if requester created at least one goal attached to this subject
    def is_user_creator_of_goal(self, request, view, action):
        try:
            requester = request.user
            subject = view.get_object()
            return subject.goals.filter(created_by=requester).exists()
        except Exception as error:
            logger.debug("SubjectAccessPolicy.is_user_creator_of_goal error: %s", error)
            return False

    # True if any goal on the subject has a student who is in a basis group taught by requester
    def is_goal_student_in_basis_group_taught_by_user(self, request, view, action):
        try:
            requester = request.user
            subject = view.get_object()
            basis_groups_taught_ids = requester.teacher_groups.filter(type='basis').values_list('id', flat=True)
            return subject.goals.filter(student__groups__id__in=basis_groups_taught_ids).exists()
        except Exception as error:
            logger.debug("SubjectAccessPolicy.is_goal_student_in_basis_group_taught_by_user error: %s", error)
            return False