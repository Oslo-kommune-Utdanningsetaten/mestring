import logging

from django.db.models import Q

from .base import BaseAccessPolicy
from mastery.models import Goal

logger = logging.getLogger(__name__)


class ObservationAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Users can list and retrieve observations according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Teachers can create observations for students they teach
        {
            "action": ["create"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_create_observation"
        },
        # Students can create observations about themselves
        {
            "action": ["create"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "can_student_create_observation"
        },
        # Students can only modify observations they created about themselves
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "can_student_modify_observation"
        },
        # Teachers can modify observations in their scope
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_modify_observation"
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        """
        Filter observations based on who can see them:
        - Everyone: Observations they created or observed (if visible)
        - Teaching group teachers: Observations on group goals in groups they teach
        - Basis group teachers: All observations for students in their basis group
        - Students: Observations about themselves (if visible)
        """
        requester = request.user
        if requester.is_superadmin:
            return qs
        try:
            teacher_group_ids = list(requester.teacher_groups.values_list('id', flat=True))
            teacher_basis_group_ids = list(requester.teacher_groups.filter(
                type='basis').values_list('id', flat=True))
            student_group_ids = list(requester.student_groups.values_list('id', flat=True))

            # Everyone can see observations they created or observed
            filters = Q(created_by=requester)
            filters |= Q(observer=requester, is_visible_to_student=True)

            # Teaching group teachers: Observations on group goals in groups they teach
            if teacher_group_ids:
                filters |= Q(goal__group_id__in=teacher_group_ids)

            # Basis teachers: All observations for students in their basis group
            if teacher_basis_group_ids:
                filters |= Q(student__groups__id__in=teacher_basis_group_ids)

            # Students: Observations about themselves (if visible)
            if student_group_ids:
                filters |= Q(student=requester, is_visible_to_student=True)

            return qs.filter(filters).distinct()
        except Exception as error:
            logger.error("ObservationAccessPolicy.scope_queryset error: %s", error)
            return qs.none()

    def can_teacher_create_observation(self, request, view, action):
        """
        Teachers can create observations based on goal type:
        - Group goal observations: Must teach that group
        - Personal goal observations: Must be basis group teacher for that student
        """
        try:
            goal_id = request.data.get("goal") or request.data.get("goal_id")
            requester = request.user

            if not goal_id:
                return False

            goal = Goal.objects.get(id=goal_id)

            # Group goal: Must teach that group
            if goal.group_id:
                return requester.teacher_groups.filter(id=goal.group_id).exists()

            # Personal goal: Must be basis group teacher
            if goal.student_id:
                return requester.teacher_groups.filter(
                    type='basis',
                    members__id=goal.student_id
                ).exists()

            return False

        except Exception as error:
            logger.error("ObservationAccessPolicy.can_teacher_create_observation error: %s", error)
            return False

    def can_student_create_observation(self, request, view, action):
        """Students can only create observations about themselves."""
        try:
            student_id = request.data.get("student") or request.data.get("student_id")
            requester = request.user

            return str(student_id) == str(requester.id)
        except Exception as error:
            logger.error("ObservationAccessPolicy.can_student_create_observation error: %s", error)
            return False

    def can_student_modify_observation(self, request, view, action):
        """Students can only modify observations they created about themselves."""
        try:
            target_observation = view.get_object()
            requester = request.user

            return (target_observation.created_by_id == requester.id and
                    target_observation.student_id == requester.id)
        except Exception as error:
            logger.error("ObservationAccessPolicy.can_student_modify_observation error: %s", error)
            return False

    def can_teacher_modify_observation(self, request, view, action):
        """
        Teachers can modify observations based on goal type:
        - Group goal observations: Must teach that group
        - Personal goal observations: Must be basis group teacher for that student
        """
        try:
            target_observation = view.get_object()
            requester = request.user

            # Group goal: Must teach that group
            if target_observation.goal and target_observation.goal.group_id:
                return requester.teacher_groups.filter(id=target_observation.goal.group_id).exists()

            # Personal goal: Must be basis group teacher
            basis_group_ids = requester.teacher_groups.filter(type='basis').values_list('id', flat=True)
            return target_observation.student.groups.filter(id__in=basis_group_ids).exists()

        except Exception as error:
            logger.error("ObservationAccessPolicy.can_teacher_modify_observation error: %s", error)
            return False
