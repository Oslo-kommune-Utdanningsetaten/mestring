import logging

from django.db.models import (
    Q,
)

from .base import (
    BaseAccessPolicy,
)

logger = logging.getLogger(__name__)


class ObservationAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Users can list observations according to scope_queryset
        {
            "action": ["list"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Users can retrieve observations they have created
        {
            "action": ["retrieve"],
            "principal": [
                "authenticated",
            ],
            "effect": "allow",
            "condition": "is_user_creator_or_observer",
        },
        # Students can retrieve observations they are the target of
        {
            "action": ["retrieve"],
            "principal": ["role:student"],
            "effect": "allow",
            "condition": "is_user_target",
        },
        # Students cannot retrieve observations that are not visible to them
        {
            "action": ["retrieve"],
            "principal": ["role:student"],
            "effect": "deny",
            "condition": "is_observation_not_visible_to_student",
        },
        # Teachers can retrieve observations for students they teach (basis or the relevant teaching group)
        {
            "action": ["retrieve"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": "is_user_teacher_of_student",
        },
        # Everyone else: implicitly denied
    ]

    def scope_queryset(self, request, qs):
        requester = request.user
        if requester.is_superadmin:
            return qs
        try:
            # Groups (any type) where requester is a teacher
            teacher_group_ids = list(
                requester.teacher_groups.values_list(
                    "id",
                    flat=True,
                )
            )
            # Basis groups where requester is a teacher
            teacher_basis_group_ids = list(
                requester.teacher_groups.filter(type="basis").values_list(
                    "id",
                    flat=True,
                )
            )

            filters = (
                # Creator or observer
                Q(created_by_id=requester.id) |
                Q(observer_id=requester.id) |
                # Students: own observations that are visible to them
                Q(student_id=requester.id, is_visible_to_student=True)
            )

            # Teachers: observations on group goals in groups they teach (basis or teaching)
            if teacher_group_ids:
                filters |= Q(goal__group_id__in=teacher_group_ids)

            # Teachers: any observations for students in basis groups they teach
            if teacher_basis_group_ids:
                filters |= Q(student__groups__id__in=teacher_basis_group_ids)

            return qs.filter(filters).distinct()
        except Exception as error:
            logger.error(f"Observation query failed : {error}")
            return qs.none()

    def is_user_creator_or_observer(self, request, view, action):
        try:
            requester = request.user
            observation = view.get_object()
            return (observation.created_by_id == requester.id) or (observation.observer_id == requester.id)
        except Exception as error:
            logger.error("ObservationAccessPolicy.is_user_creator_or_observer error: %s", error)
            return False

    def is_user_target(self, request, view, action):
        try:
            requester = request.user
            observation = view.get_object()
            return observation.student_id == requester.id
        except Exception as error:
            logger.error("ObservationAccessPolicy.is_user_target error: %s", error)
            return False

    def is_observation_not_visible_to_student(self, request, view, action):
        try:
            observation = view.get_object()
            return not bool(
                observation.is_visible_to_student)
        except Exception as error:
            logger.error("ObservationAccessPolicy.is_observation_not_visible_to_student error: %s", error)
            return False

    def is_user_teacher_of_student(self, request, view, action):
        try:
            requester = request.user
            observation = view.get_object()
            # Teacher of the relevant teaching/basis group for a group goal
            teacher_group_ids = set(
                requester.teacher_groups.values_list(
                    "id",
                    flat=True,
                )
            )
            if observation.goal.group_id and observation.goal.group_id in teacher_group_ids:
                return True
            # Teacher of any basis group the student belongs to
            basis_groups_taught_ids = set(
                requester.teacher_groups.filter(type="basis").values_list(
                    "id",
                    flat=True,
                )
            )
            return observation.student.groups.filter(id__in=basis_groups_taught_ids).exists()
        except Exception as error:
            logger.error("ObservationAccessPolicy.is_user_teacher_of_student error: %s", error)
            return False
