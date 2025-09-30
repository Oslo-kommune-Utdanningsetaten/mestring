from mastery.models import Goal
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
        # # Authenticated users can list goals according to scope_queryset
        # {
        #     "action": ["list"],
        #     "principal": ["authenticated"],
        #     "effect": "allow",
        # },
        # # Authenticated users can retrieve goals they have created
        # {
        #     "action": ["retrieve"],
        #     "principal": ["authenticated"],
        #     "effect": "allow",
        #     "condition": "is_user_creator"
        # },
        # # Teacher can retrieve group goals for the groups they teach
        # {
        #     "action": ["retrieve"],
        #     "principal": ["role:teacher"],
        #     "effect": "allow",
        #     "condition": "is_goal_in_group_where_user_is_teacher"
        # },
        # # Teacher can retrieve personal goals where the student is in a group they teach
        # {
        #     "action": ["retrieve"],
        #     "principal": ["role:teacher"],
        #     "effect": "allow",
        #     "condition": "is_goal_student_in_group_taught_by_user"
        # },
        # # Student can retrieve personal goals they own
        # {
        #     "action": ["retrieve"],
        #     "principal": ["role:student"],
        #     "effect": "allow",
        # "condition": "is_user_owner"
        # },
        # # Student can retrieve group goals where they are a student
        # {
        #     "action": ["retrieve"],
        #     "principal": ["role:student"],
        #     "effect": "allow",
        #     "condition": "is_goal_in_group_where_user_is_student"
        # },
        # Students can create personal goals for themselves
        {
            "action": ["create"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_creating_personal_goal_for_self"
        },
        # Teachers can create goals
        {
            "action": ["create"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_teacher_creating_valid_goal"
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
        requester = request.user
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
        except Exception as error:
            logger.error("GoalAccessPolicy.scope_queryset error: %s", error)
            return qs.none()

    def is_user_creator(self, request, view, action):
        try:
            requester = request.user
            goal = view.get_object()
            return goal.created_by_id == requester.id
        except Exception as error:
            logger.error("GoalAccessPolicy.is_user_creator error: %s", error)
            return False

    def is_goal_in_group_where_user_is_teacher(self, request, view, action):
        try:
            requester = request.user
            goal = view.get_object()
            if goal.group_id is None:
                return False
            return requester.teacher_groups.filter(id=goal.group_id).exists()
        except Exception as error:
            logger.error(
                "GoalAccessPolicy.is_goal_in_group_where_user_is_teacher error: %s", error)
            return False

    def is_goal_student_in_group_taught_by_user(self, request, view, action):
        try:
            requester = request.user
            goal = view.get_object()
            if goal.student_id is None:
                return False
            taught_group_ids = requester.teacher_groups.values_list(
                'id', flat=True)
            return goal.student.groups.filter(id__in=taught_group_ids).exists()
        except Exception as error:
            logger.error(
                "GoalAccessPolicy.is_goal_student_in_group_taught_by_user error: %s", error)
            return False

    def is_user_owner(self, request, view, action):
        try:
            requester = request.user
            goal = view.get_object()
            return goal.student_id == requester.id
        except Exception as error:
            logger.error("GoalAccessPolicy.is_user_owner error: %s", error)
            return False

    def is_goal_in_group_where_user_is_student(self, request, view, action):
        try:
            requester = request.user
            goal = view.get_object()
            if goal.group_id is None:
                return False
            return requester.student_groups.filter(id=goal.group_id).exists()
        except Exception as error:
            logger.error(
                "GoalAccessPolicy.is_goal_in_group_where_user_is_student error: %s", error)
            return False

    def is_creating_personal_goal_for_self(self, request, view, action):
        try:
            requester = request.user
            # Check both possible field names (student_id from serializer, student from form data)
            student_id = request.data.get('student_id') or request.data.get('student')
            group_id = request.data.get('group_id') or request.data.get('group')

            logger.debug(f"Debug goal creation: student_id={student_id}, group_id={group_id}, requester_id={requester.id}, request_data={request.data}")

            # Must be creating a personal goal (not group goal)
            if group_id is not None:
                return False

            # Must be creating for themselves
            return str(student_id) == str(requester.id)
        except Exception as error:
            logger.error("GoalAccessPolicy.is_creating_personal_goal_for_self error: %s", error)
            return False

    def is_teacher_creating_valid_goal(self, request, view, action):
        try:
            requester = request.user
            # Check both possible field names (student_id from serializer, student from form data)
            student_id = request.data.get('student_id') or request.data.get('student')
            group_id = request.data.get('group_id') or request.data.get('group')

            # Teachers can create group goals for groups they teach
            if group_id is not None:
                return requester.teacher_groups.filter(id=group_id).exists()

            # Teachers can create personal goals for students they teach
            if student_id is not None:
                taught_group_ids = requester.teacher_groups.values_list('id', flat=True)
                from mastery.models import User
                try:
                    student = User.objects.get(id=student_id)
                    return student.student_groups.filter(id__in=taught_group_ids).exists()
                except User.DoesNotExist:
                    return False

            return False
        except Exception as error:
            logger.error("GoalAccessPolicy.is_teacher_creating_valid_goal error: %s", error)
            return False

    def can_student_modify_goal(self, request, view, action):
        try:
            target_goal = view.get_object()
            requester = request.user
            # Students can only modify their own personal goals (not group goals)
            return target_goal.student_id == requester.id and target_goal.group_id is None
        except Exception as error:
            logger.error("GoalAccessPolicy.can_student_modify_goal error: %s", error)
            return False

    def can_teacher_modify_goal(self, request, view, action):
        try:
            target_goal = view.get_object()
            # Teachers can modify any goal in their scope (reuse scope_queryset logic)
            #TODO: Discuss if teacher should be able to modify personal goals of students they teach
            return self.scope_queryset(request, Goal.objects).filter(id=target_goal.id).exists()
        except Exception as error:
            logger.error("GoalAccessPolicy.can_teacher_modify_goal error: %s", error)
            return False
      