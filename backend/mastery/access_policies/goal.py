from .base import BaseAccessPolicy
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)


class GoalAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Authenticated users can list and retrieve goals (filtered by scope_queryset)
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Students can create personal goals for themselves
        {
            "action": ["create"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "can_student_create_goal"
        },
        # Teachers can create goals
        {
            "action": ["create"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_create_goal"
        },
        # Students can only modify their own personal goals
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "can_student_modify_goal"
        },
        # Teachers can modify goals in their scope
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_modify_goal"
        }
    ]

    def scope_queryset(self, request, qs):
        """
        Filter goals based on who can see them:
        - Everyone: Goals they created
        - Teaching group teachers: Group goals in groups they teach
        - Basis group teachers: Personal goals + group goals for students in their basis group
        - Students: Their own personal goals + group goals in groups they're in
        """
        requester = request.user
        if requester.is_superadmin:
            return qs
        try:
            teacher_group_ids = list(
                requester.teacher_groups.values_list('id', flat=True))
            teacher_basis_group_ids = list(
                requester.teacher_groups.filter(type='basis').values_list('id', flat=True))
            student_group_ids = list(
                requester.student_groups.values_list('id', flat=True))

            # Everyone can see goals they created
            filters = Q(created_by=requester)

            # Teaching group teachers: Group goals in groups they teach
            if teacher_group_ids:
                filters |= Q(group_id__in=teacher_group_ids)

            # Basis group teachers: All goals for students in their basis group
            if teacher_basis_group_ids:
                filters |= Q(student__groups__id__in=teacher_basis_group_ids)
                filters |= Q(group__members__groups__id__in=teacher_basis_group_ids)

            # Students: Own personal goals + group goals in their groups
            if student_group_ids:
                filters |= Q(student=requester)
                filters |= Q(group_id__in=student_group_ids)

            return qs.filter(filters).distinct()
        except Exception as error:
            logger.error("GoalAccessPolicy.scope_queryset error: %s", error)
            return qs.none()

    def can_student_create_goal(self, request, view, action):
        """Students can only create personal goals for themselves."""
        try:
            requester = request.user
            student_id = request.data.get('student_id') or request.data.get('student')
            group_id = request.data.get('group_id') or request.data.get('group')

            # Must be creating a personal goal
            if group_id is not None:
                return False

            # Must be creating for themselves
            return str(student_id) == str(requester.id)
        except Exception as error:
            logger.error("GoalAccessPolicy.can_student_create_goal error: %s", error)
            return False

    def can_teacher_create_goal(self, request, view, action):
        """
        Teachers can create goals based on goal type:
        - Group goals: Must teach that group
        - Personal goals: Must be basis group teacher for that student
        """
        try:
            requester = request.user
            student_id = request.data.get('student_id') or request.data.get('student')
            group_id = request.data.get('group_id') or request.data.get('group')

            # Group goal: Must teach that group
            if group_id is not None:
                return requester.teacher_groups.filter(id=group_id).exists()

            # Personal goal: Must be basis group teacher
            if student_id is not None:
                return requester.teacher_groups.filter(
                    type='basis',
                    members__id=student_id
                ).exists()

            return False
        except Exception as error:
            logger.error("GoalAccessPolicy.can_teacher_create_goal error: %s", error)
            return False

    def can_student_modify_goal(self, request, view, action):
        """Students can only modify their own personal goals."""
        try:
            target_goal = view.get_object()
            requester = request.user
            return target_goal.student_id == requester.id and target_goal.group_id is None
        except Exception as error:
            logger.error("GoalAccessPolicy.can_student_modify_goal error: %s", error)
            return False

    def can_teacher_modify_goal(self, request, view, action):
        """
        Teachers can modify goals based on goal type:
        - Group goals: Must teach that group
        - Personal goals: Must be basis group teacher for that student
        """
        try:
            target_goal = view.get_object()
            requester = request.user

            # Group goal: Must teach that group
            if target_goal.group_id:
                return requester.teacher_groups.filter(id=target_goal.group_id).exists()

            # Personal goal: Must be basis group teacher
            basis_group_ids = requester.teacher_groups.filter(type='basis').values_list('id', flat=True)
            return target_goal.student.groups.filter(id__in=basis_group_ids).exists()
        except Exception as error:
            logger.error("GoalAccessPolicy.can_teacher_modify_goal error: %s", error)
            return False
