import logging
from django.db.models import Q, Exists, OuterRef
from django.utils import timezone
from .base import BaseAccessPolicy
from mastery.models import UserGroup, UserSchool
from ..api.school_year_functions import is_entity_from_current_school_year


logger = logging.getLogger(__name__)


class StatusAccessPolicy(BaseAccessPolicy):
    statements = [
        # Superadmin: full access
        {
            "action": ["*"],
            "principal": ["role:superadmin"],
            "effect": "allow",
        },
        # Users can list and retrieve statuses according to scope_queryset
        {
            "action": ["list", "retrieve"],
            "principal": ["authenticated"],
            "effect": "allow",
        },
        # Teachers can create statuses for students they teach
        {
            "action": ["create"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": ["can_teacher_create_status", "is_status_from_current_school_year"]
        },
        # Teachers can modify statuses for and students they teach
        {
            "action": ["update", "partial_update", "destroy"],
            "principal": ["role:teacher"],
            "effect": "allow",
            "condition": ["can_teacher_modify_status", "is_status_from_current_school_year"]
        },
        # School admins can CRUD statuses belonging to their school
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
        Filter statuses based on who can see them:
        - Everyone: Statuses they created
        - School inspectors and admins: All statuses at their schools
        - Teaching group teachers:
          - Statuses on group goals in groups they teach
          - Statuses on individual goals for students they teach in that subject
        - Basis group teachers: Statuses for students in their basis group
        - Students: Statuses about themselves, if current date is after end_at
        """
        requester = request.user
        if not requester:
            return qs.none()
        if requester.is_superadmin:
            return qs
        try:
            teacher_group_ids = list(requester.teacher_groups.filter(
                type='teaching').values_list('id', flat=True))
            teacher_basis_group_ids = list(requester.teacher_groups.filter(
                type='basis').values_list('id', flat=True))
            school_employee_ids = UserSchool.objects.filter(
                user_id=requester.id, role__name__in=["admin", "inspector"]).values_list(
                "school_id", flat=True).distinct()

            # Everyone can see statuses they created
            filters = Q(created_by=requester)

            # School inspectors and admins: All statuses at their schools
            if school_employee_ids:
                # Statuses at their schools
                filters |= Q(school_id__in=school_employee_ids)

            # Teaching group teachers: Statuses for students they teach, in those subjects only
            if teacher_group_ids:
                # Memberships where teacher teaches, student is member, and group subject matches status subject
                memberships_in_teacher_group_on_subject = UserGroup.objects.filter(
                    user_id=OuterRef('student_id'),
                    group_id__in=teacher_group_ids,
                    group__subject_id=OuterRef('subject_id'),
                    group__school_id=OuterRef('school_id'),
                )
                qs = qs.annotate(teacher_teaches_student_subject=Exists(
                    memberships_in_teacher_group_on_subject))
                filters |= Q(student__isnull=False, teacher_teaches_student_subject=True)

            # Basis teachers: All statuses for students in their basis group at the same school
            if teacher_basis_group_ids:
                overlapping_basis_memberships = UserGroup.objects.filter(
                    user_id=OuterRef('student_id'),
                    group_id__in=teacher_basis_group_ids,
                    group__school_id=OuterRef('school_id'),
                )
                qs = qs.annotate(student_in_basis_group=Exists(overlapping_basis_memberships))
                filters |= Q(student_in_basis_group=True)

            # Students: Statuses about themselves, if current date is after end_at
            filters |= Q(student=requester, end_at__lt=timezone.now())

            return qs.filter(filters).distinct()
        except Exception:
            logger.exception("StatusAccessPolicy.scope_queryset")
            return qs.none()

    def can_teacher_create_status(self, request, view, action):
        """
        Teachers can create statuses for students they teach, in that subject.
        Basis group teachers can create statuses without a subject (with a category)
        for students in their basis group.
        """
        try:
            student_id = request.data.get("student_id")
            subject_id = request.data.get("subject_id")
            school_id = request.data.get("school_id")
            requester = request.user

            if not student_id:
                return False

            if subject_id:
                # Teachers that teach the subject to that student
                return requester.teacher_groups.filter(
                    subject_id=subject_id,
                    members__id=student_id,
                    school_id=school_id
                ).exists()

            # No subject: allow if teacher is in a basis group with the student at this school
            return requester.teacher_groups.filter(
                type='basis',
                members__id=student_id,
                school_id=school_id
            ).exists()

        except Exception:
            logger.exception("StatusAccessPolicy.can_teacher_create_status")
            return False

    def can_teacher_modify_status(self, request, view, action):
        """
        Teachers can modify status if they teach the subject to that student.
        Basis group teachers can modify statuses without a subject for students
        in their basis group.
        """
        try:
            target_status = view.get_object()
            requester = request.user
            school_id = target_status.school_id

            if target_status.subject_id:
                return requester.teacher_groups.filter(
                    subject_id=target_status.subject_id,
                    members__id=target_status.student_id,
                    school_id=school_id
                ).exists()

            # No subject: allow if teacher is in a basis group with the student
            return requester.teacher_groups.filter(
                type='basis',
                members__id=target_status.student_id,
                school_id=school_id
            ).exists()

        except Exception:
            logger.exception("StatusAccessPolicy.can_teacher_modify_status")
            return False

    # True if requester is admin at the school which owns the status
    def is_admin_at_school(self, request, view, action):
        try:
            if action == 'create':
                school_id = request.data.get("school_id")
            elif action in ['update', 'partial_update', 'destroy']:
                status = view.get_object()
                if not status:
                    return False
                school_id = status.school_id

            if not school_id:
                return False

            school_admin_ids = UserSchool.objects.filter(
                user_id=request.user.id, role__name="admin").values_list("school_id", flat=True).distinct()

            return school_id in school_admin_ids

        except Exception:
            logger.exception("StatusAccessPolicy.is_admin_at_school")
            return False

    def is_status_from_current_school_year(self, request, view, action):
        if action == 'create':
            return True
        else:
            try:
                status = view.get_object()
                return is_entity_from_current_school_year(status)
            except Exception:
                logger.exception("StatusAccessPolicy.is_status_from_current_school_year")
                return False
