import logging
from django.db.models import Q, Exists, OuterRef
from .base import BaseAccessPolicy
from mastery.models import Goal, UserGroup, UserSchool

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
        # Teachers can modify observations they created and according to goal type and students they teach
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "can_teacher_modify_observation"
        },
        # School admins can CRUD observations for students at their school
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
        Filter observations based on who can see them:
        - Everyone: Observations they created or observed (if visible)
        - School inspectors and admins: All observations with goals at their schools
        - Teaching group teachers:
          - Observations on group goals in groups they teach
          - Observations on individual goals for students they teach in that subject
        - Basis group teachers: All observations for students in their basis group
        - Students: Observations about themselves (if visible)
        """
        requester = request.user
        if not requester:
            return qs.none()
        if requester.is_superadmin:
            return qs
        try:
            teacher_teaching_group_ids = list(requester.teacher_groups.filter(
                type='teaching').values_list('id', flat=True))
            teacher_basis_group_ids = list(requester.teacher_groups.filter(
                type='basis').values_list('id', flat=True))
            school_employee_ids = UserSchool.objects.filter(
                user_id=requester.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            # Everyone can see observations they created or observed
            filters = Q(created_by=requester)
            filters |= Q(observer=requester, is_visible_to_student=True)

            # School inspectors and admins: All observations for goals at their schools
            if school_employee_ids:
                # Observations on goals at their schools
                filters |= Q(goal__school_id__in=school_employee_ids)

            # Teaching group teachers: Observations on group goals + individual goals for students they teach
            if teacher_teaching_group_ids:
                # Observations on group goals in groups they teach
                filters |= Q(goal__group_id__in=teacher_teaching_group_ids)

                # Observations on individual goals where teacher teaches that subject to that student
                memberships_in_teacher_group_on_subject = UserGroup.objects.filter(
                    user_id=OuterRef('goal__student_id'),
                    group_id__in=teacher_teaching_group_ids,
                    group__subject_id=OuterRef('goal__subject_id'),
                )
                qs = qs.annotate(teacher_teaches_student_subject=Exists(
                    memberships_in_teacher_group_on_subject))
                filters |= Q(goal__student__isnull=False, teacher_teaches_student_subject=True)

            # Basis teachers: All observations for students in their basis group
            if teacher_basis_group_ids:
                filters |= Q(student__groups__id__in=teacher_basis_group_ids)

            # Students: Observations about themselves (if visible)
            filters |= Q(student=requester, is_visible_to_student=True)

            return qs.filter(filters).distinct()
        except Exception:
            logger.exception("ObservationAccessPolicy.scope_queryset")
            return qs.none()

    def can_teacher_create_observation(self, request, view, action):
        """
        Teachers can create observations based on goal type:
        - Group goal observations: Must teach that group
        - Individual goal observations: Must be basis group teacher OR teach that subject to that student
        """
        try:
            goal_id = request.data.get("goal_id")
            requester = request.user

            if not goal_id:
                return False

            # Fetch only the fields needed for permission check
            goal = Goal.objects.filter(id=goal_id).values(
                'group_id', 'student_id', 'subject_id'
            ).first()
            if not goal:
                return False

            # Group goal: Must teach that group
            if goal['group_id']:
                return requester.teacher_groups.filter(id=goal['group_id']).exists()

            # Individual goal: Basis group teacher OR teaches that subject to that student
            if goal['student_id']:
                is_basis_teacher = requester.teacher_groups.filter(
                    type='basis',
                    members__id=goal['student_id']
                ).exists()

                teaches_subject = requester.teacher_groups.filter(
                    subject_id=goal['subject_id'],
                    members__id=goal['student_id']
                ).exists()

                return is_basis_teacher or teaches_subject

            return False

        except Exception:
            logger.exception("ObservationAccessPolicy.can_teacher_create_observation")
            return False

    def can_student_create_observation(self, request, view, action):
        """Students can only create observations about themselves."""
        try:
            student_id = request.data.get("student_id")
            requester = request.user

            # Force it so that students cannot create invisible observations
            request.data['is_visible_to_student'] = True

            return str(student_id) == str(requester.id)
        except Exception:
            logger.exception("ObservationAccessPolicy.can_student_create_observation")
            return False

    def can_student_modify_observation(self, request, view, action):
        """Students can only modify observations they created about themselves."""
        try:
            target_observation = view.get_object()
            requester = request.user

            return (target_observation.created_by_id == requester.id and
                    target_observation.student_id == requester.id)
        except Exception:
            logger.exception("ObservationAccessPolicy.can_student_modify_observation")
            return False

    def can_teacher_modify_observation(self, request, view, action):
        """
        Teachers can modify observations based on goal type and ownership:
        - Must be the creator of the observation OR have created_by is None
        - Group goal observations: Must teach that group
        - Individual goal observations: Must be basis group teacher OR teach that subject to that student
        """
        try:
            target_observation = view.get_object()
            requester = request.user

            # Teachers can only modify observations they created or observations with no creator
            if target_observation.created_by_id != requester.id:
                return False

            # Get goal info without loading the full object
            goal = Goal.objects.filter(id=target_observation.goal_id).values(
                'group_id', 'subject_id', 'school_id'
            ).first()
            if not goal:
                return False

            # Group goal: Must teach that group
            if goal['group_id']:
                return requester.teacher_groups.filter(id=goal['group_id']).exists()

            # Individual goal: Basis group teacher OR teaches that subject to that student
            basis_group_ids = requester.teacher_groups.filter(
                type='basis', school_id=goal['school_id']).values_list(
                'id', flat=True)
            is_basis_teacher = UserGroup.objects.filter(
                user_id=target_observation.student_id,
                group_id__in=basis_group_ids
            ).exists()

            teaches_subject_at_school = requester.teacher_groups.filter(
                subject_id=goal['subject_id'],
                members__id=target_observation.student_id,
                school_id=goal['school_id']
            ).exists()

            return is_basis_teacher or teaches_subject_at_school

        except Exception:
            logger.exception("ObservationAccessPolicy.can_teacher_modify_observation")
            return False

    # True if requester is admin at the school which owns the observation
    def is_admin_at_school(self, request, view, action):
        try:
            if action == 'create':
                goal_id = request.data.get("goal_id")
                if not goal_id:
                    return False
                school_id = Goal.objects.filter(id=goal_id).values_list('school_id', flat=True).first()
            elif action in ['update', 'partial_update', 'destroy']:
                observation = view.get_object()
                if not observation or not observation.goal_id:
                    return False
                school_id = Goal.objects.filter(
                    id=observation.goal_id).values_list(
                    'school_id', flat=True).first()
            else:
                return False

            if not school_id:
                return False

            school_admin_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name="admin").values_list("school_id", flat=True).distinct()

            return school_id in school_admin_ids

        except Exception:
            logger.exception("ObservationAccessPolicy.is_admin_at_school")
            return False
