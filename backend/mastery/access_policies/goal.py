from .base import BaseAccessPolicy
from mastery.models import Subject, UserGroup, UserSchool, Group
from django.db.models import Q, Exists, OuterRef
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
        # Authenticated users can list and retrieve goals filtered by scope_queryset
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
        # Teachers can modify goals they have created and according to students and groups they teach
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_modify_goal"
        },
        # School admins have write access to goals belonging to their school
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["role:admin"],
            "effect": "allow",
            "condition": "is_admin_at_school"
        },
    ]

    def scope_queryset(self, request, qs):
        """
        Filter goals based on who can see them:
        - Everyone: Goals they created
        - School inspectors: All goals for students at their schools
        - Teaching group teachers:
          - Group goals in groups they teach
          - Personal goals for students they teach in that subject
        - Basis group teachers: Personal goals + group goals for students in their basis group
        - Students: Their own personal goals + group goals in groups they're in
        """
        requester = request.user
        if not requester:
            return qs.none()
        if requester.is_superadmin:
            return qs
        try:
            teacher_group_ids = list(
                requester.teacher_groups.values_list('id', flat=True))
            teacher_basis_group_ids = list(
                requester.teacher_groups.filter(type='basis').values_list('id', flat=True))
            student_group_ids = list(
                requester.student_groups.values_list('id', flat=True))
            school_affiliated_ids = UserSchool.objects.filter(
                user_id=requester.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            # Everyone can see goals they created
            filters = Q(created_by=requester)

            # School inspectors and admins: All goals for students at their schools
            if school_affiliated_ids:
                # Goals for groups at their schools
                filters |= Q(group__school_id__in=school_affiliated_ids)
                # Goals for subjects owned by their schools
                filters |= Q(subject__owned_by_school_id__in=school_affiliated_ids)

            # Teaching group teachers: Group goals + personal goals for students they teach
            if teacher_group_ids:
                # Group goals in groups they teach
                filters |= Q(group_id__in=teacher_group_ids)

                # Check if teacher teaches the subject to the student
                student_in_teacher_subject = UserGroup.objects.filter(
                    user_id=OuterRef('student_id'),  # Student from the goal
                    group_id__in=teacher_group_ids,  # Groups the teacher teaches
                    group__subject_id=OuterRef('subject_id'),  # Subject from the goal
                )

                qs = qs.annotate(teacher_teaches_student_subject=Exists(student_in_teacher_subject))
                filters |= Q(student__isnull=False, teacher_teaches_student_subject=True)

            # Basis group teachers: All goals for students in their basis group
            if teacher_basis_group_ids:
                filters |= Q(student__groups__id__in=teacher_basis_group_ids)
                filters |= Q(group__members__groups__id__in=teacher_basis_group_ids)

            # Students: Own personal goals + group goals in their groups
            filters |= Q(student=requester)
            if student_group_ids:
                filters |= Q(group_id__in=student_group_ids)

            return qs.filter(filters).distinct()
        except Exception:
            logger.exception("GoalAccessPolicy.scope_queryset error")
            return qs.none()

    def can_student_create_goal(self, request, view, action):
        """Students can only create personal goals for themselves."""
        try:
            requester = request.user
            student_id = request.data.get('student_id')
            group_id = request.data.get('group_id')

            # Must be creating a personal goal
            if group_id is not None:
                return False

            # Must be creating for themselves
            return str(student_id) == str(requester.id)
        except Exception:
            logger.exception("GoalAccessPolicy.can_student_create_goal error")
            return False

    def can_teacher_create_goal(self, request, view, action):
        """
        Teachers can create goals based on goal type:
        - Group goals: Must teach that group
        - Personal goals: Must be basis group teacher OR teach that subject to that student
        """
        try:
            requester = request.user
            student_id = request.data.get('student_id')
            group_id = request.data.get('group_id')

            # Group goal: Must teach that group
            if group_id is not None:
                return requester.teacher_groups.filter(id=group_id).exists()

            # Personal goal: Basis group teacher OR teaches that subject to that student
            if student_id is not None:
                subject_id = request.data.get('subject_id') or request.data.get('subject')

                # Check if basis group teacher for this student
                is_basis_teacher = requester.teacher_groups.filter(
                    type='basis',
                    members__id=student_id
                ).exists()

                # Check if teaches this subject to this student
                teaches_subject = requester.teacher_groups.filter(
                    subject_id=subject_id,
                    members__id=student_id
                ).exists()

                return is_basis_teacher or teaches_subject

            return False
        except Exception:
            logger.exception("GoalAccessPolicy.can_teacher_create_goal error")
            return False

    def can_student_modify_goal(self, request, view, action):
        """Students can only modify their own personal goals as long as they have created them."""
        try:
            target_goal = view.get_object()
            requester = request.user
            return (target_goal.student_id == requester.id and
                    target_goal.group_id is None and
                    target_goal.created_by_id == requester.id)
        except Exception as error:
            logger.exception("GoalAccessPolicy.can_student_modify_goal error")
            return False

    def can_teacher_modify_goal(self, request, view, action):
        """
        Teachers can modify goals based on goal type:
        - Group goals: Must teach that group
        - Personal goals: Must be basis group teacher OR teach that subject to that student
        """
        try:
            target_goal = view.get_object()
            requester = request.user

            if target_goal.created_by_id != requester.id:
                # Teachers can only modify goals they created
                return False

            # Group goal: Must teach that group
            if target_goal.group_id:
                return requester.teacher_groups.filter(id=target_goal.group_id).exists()

            # Personal goal: Basis group teacher OR teaches that subject to that student
            basis_group_ids = requester.teacher_groups.filter(type='basis').values_list('id', flat=True)
            is_basis_teacher = target_goal.student.groups.filter(id__in=basis_group_ids).exists()

            # Check if teaches this subject to this student
            teaches_subject = requester.teacher_groups.filter(
                subject=target_goal.subject,
                members__id=target_goal.student_id
            ).exists()

            return is_basis_teacher or teaches_subject
        except Exception:
            logger.exception("GoalAccessPolicy.can_teacher_modify_goal error")
            return False

    # True if requester is admin at the school which owns the goal
    def is_admin_at_school(self, request, view, action):
        try:
            if action == 'create':
                group_id = request.data.get("group_id")
                subject_id = request.data.get("subject_id")
                if group_id:
                    # Get school from group
                    group = Group.objects.get(id=group_id)
                    school_id = group.school_id
                elif subject_id:
                    # Get school from subject
                    subject = Subject.objects.get(id=subject_id)
                    school_id = subject.owned_by_school_id
                else:
                    return False

            elif action in ['update', 'partial_update', 'destroy']:
                goal = view.get_object()
                if not goal:
                    return False
                if goal.group_id:
                    # Get school from group
                    school_id = goal.group.school_id
                else:
                    # Get school from subject
                    school_id = goal.subject.owned_by_school_id
            else:
                return False

            # No school associated, deny access
            if not school_id:
                return False

            school_admin_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name="admin").values_list("school_id", flat=True).distinct()

            return school_id in school_admin_ids

        except Exception:
            logger.exception("SubjectAccessPolicy.belongs_to_group error")
            return False
