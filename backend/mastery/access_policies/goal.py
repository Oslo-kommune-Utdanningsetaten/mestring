from .base import BaseAccessPolicy
from django.db.models import Q
from mastery.models import Goal
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
        # Authenticated users can list goals according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Authenticated users can retrieve goals they have created
        {
            "action": ["retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
            "condition": "is_user_creator"
        },
        # Teacher can retrieve group goals for the groups they teach
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_goal_in_group_where_user_is_teacher"
        },
        # Teacher can retrieve personal goals where the student is in a group they teach
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_goal_student_in_group_taught_by_user"
        },
        # Student can retrieve personal goals they own
        {
            "action": ["retrieve"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_user_owner"
        },
        # Student can retrieve group goals where they are a student
        {
            "action": ["retrieve"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_goal_in_group_where_user_is_student"
        }
    ]

    def scope_queryset(self, request, qs):
        requester = request.user
        if not requester:
            return qs.none()
        if requester.is_superadmin:
            return qs
        try:
            teacher_group_ids = list(
                requester.teacher_groups.values_list('id', flat=True))
            student_group_ids = list(
                requester.student_groups.values_list('id', flat=True))
            # All users can see goals created by self
            filters = Q(created_by=requester)

            # Teacher-related visibility
            if teacher_group_ids:
                # group goals in groups they teach
                filters |= Q(group_id__in=teacher_group_ids)
                # personal goals where student in taught group
                filters |= Q(student__groups__id__in=teacher_group_ids)

            # Student-related visibility
            if student_group_ids:
                # Personal goals they own
                filters |= Q(student=requester)
                # Group goals where they are a (student) member
                filters |= Q(group_id__in=student_group_ids)

            return qs.filter(filters).distinct()
        except Exception:
            logger.exception("GoalAccessPolicy.scope_queryset error")
            return qs.none()

    def is_user_creator(self, request, view, action):
        try:
            goal_id = self.get_target_id(view)
            if not goal_id:
                return False
            qs = self.scope_queryset(request, Goal.objects)
            return qs.filter(id=goal_id, created_by_id=request.user.id).exists()
        except Exception:
            logger.exception("GoalAccessPolicy.is_user_creator error")
            return False

    def is_goal_in_group_where_user_is_teacher(self, request, view, action):
        try:
            requester = request.user
            target_goal_id = self.get_target_id(view)
            if not target_goal_id:
                return False
            goal = view.get_object()
            if goal.group_id is None:
                return False
            return requester.teacher_groups.filter(id=goal.group_id).exists()
        except Exception:
            logger.exception("GoalAccessPolicy.is_goal_in_group_where_user_is_teacher")
            return False

    def is_goal_student_in_group_taught_by_user(self, request, view, action):
        try:
            requester = request.user
            target_goal_id = self.get_target_id(view)
            if not target_goal_id:
                return False
            goal = view.get_object()
            if goal.student_id is None:
                return False
            taught_group_ids = requester.teacher_groups.values_list(
                'id', flat=True)
            return goal.student.groups.filter(id__in=taught_group_ids).exists()
        except Exception:
            logger.exception("GoalAccessPolicy.is_goal_student_in_group_taught_by_user")
            return False

    def is_user_owner(self, request, view, action):
        try:
            target_goal_id = self.get_target_id(view)
            if not target_goal_id:
                return False

            qs = self.scope_queryset(request, Goal.objects)
            return qs.filter(id=target_goal_id, student_id=request.user.id).exists()
        except Exception:
            logger.exception("GoalAccessPolicy.is_user_owner")
            return False

    def is_goal_in_group_where_user_is_student(self, request, view, action):
        try:
            requester = request.user
            target_goal_id = self.get_target_id(view)
            if not target_goal_id:
                return False
            goal = view.get_object()
            if goal.group_id is None:
                return False
            return requester.student_groups.filter(id=goal.group_id).exists()
        except Exception:
            logger.exception("GoalAccessPolicy.is_goal_in_group_where_user_is_student")
            return False
