from django.utils import timezone
from mastery import models
from django.db.models import Q, Count
from mastery.constants import (
    DAYS_BEFORE_HARD_DELETE_OF_GROUP,
    DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION,
    DAYS_BEFORE_HARD_DELETE_OF_GOAL,
    DAYS_BEFORE_HARD_DELETE_OF_USER,
    HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP,
)
import logging
logger = logging.getLogger(__name__)


# This method is typically run immediately after a data import from Feide has completed
# Should be set to run with maintained_earlier_than equal to the time the import started
# Data which should be invisible, due to not being maintained during feide import, is soft-deleted
# Data which has been soft-deleted for some time is hard-deleted
def update_data_integrity(org_number, options):

    logger.debug("Activating cleaner bot for organization: %s", org_number)

    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        raise Exception(f"School with org number {org_number} not found in database.")

    groups_earlier_than = options.get("groups_earlier_than")
    memberships_earlier_than = options.get("memberships_earlier_than")
    if not groups_earlier_than or not memberships_earlier_than:
        raise ValueError(
            "Both 'groups_earlier_than' and 'memberships_earlier_than' must be provided in options.")

    changes = {
        "group": {},
        "user": {},
        "observation": {},
        "goal": {},
        "user_group": {},
    }
    errors = []
    now = timezone.now()

    # Soft delete
    logger.debug("Begin soft-delete: %s", options)
    changes["group"]["soft-deleted"] = soft_delete_groups(school, now, groups_earlier_than)
    changes["user"]["soft-deleted"] = soft_delete_users(school, now, memberships_earlier_than)
    changes["observation"]["soft-deleted"] = soft_delete_observations(school, now)
    changes["goal"]["soft-deleted"] = soft_delete_goals(school, now)
    changes["user_group"]["soft-deleted"] = soft_delete_user_groups(school, now, memberships_earlier_than)
    logger.debug(f"End soft-delete")

    # Hard delete
    logger.debug(f"Begin hard-delete of anything soft-deleted a sufficiently long time ago")
    changes["group"]["hard-deleted"] = hard_delete_groups(school, now)
    changes["user"]["hard-deleted"] = hard_delete_users(school, now)
    changes["observation"]["hard-deleted"] = hard_delete_observations(school, now)
    changes["goal"]["hard-deleted"] = hard_delete_goals(school, now)
    changes["user_group"]["hard-deleted"] = hard_delete_user_groups(school, now)
    logger.debug(f"End hard-delete")

    yield {
        "result": {
            "entity": "all",
            "action": "update_data_integrity",
            "errors": errors,
            "changes": changes,
        },
        "is_done": True,
    }


def soft_delete_groups(school, now, maintained_earlier_than):
    # If not maintained since maintained_earlier_than AND not deleted AND group is valid -> mark as deleted
    # Note: DO NOT mess with invalid groups
    groups = models.Group.objects.filter(
        deleted_at__isnull=True,
        school=school,
        maintained_at__lt=maintained_earlier_than
    ).within_validity_period()
    count = groups.count()
    groups.update(deleted_at=now)
    return count


def soft_delete_users(school, now, maintained_earlier_than):
    # If not superadmin AND not maintained since maintained_earlier_than AND no non-deleted UserGroups -> mark as deleted
    # Note: Users are school-agnostic, but only consider users linked to this school via UserGroups
    users = models.User.objects.annotate(
        active_user_groups_count=Count('user_groups',
                                       filter=Q(user_groups__deleted_at__isnull=True))
    ).filter(
        deleted_at__isnull=True,
        user_groups__group__school=school,
        is_superadmin=False,
        maintained_at__lt=maintained_earlier_than,
        active_user_groups_count=0
    )
    count = users.count()
    users.update(deleted_at=now)
    return count


def soft_delete_observations(school, now):
    # If student is soft-deleted -> mark as deleted
    on_personal_goals_on_school = Q(
        goal__student__isnull=False,
        goal__subject__owned_by_school=school
    )
    on_group_goals_on_school = Q(goal__group__school=school)
    observations = models.Observation.objects.filter(
        deleted_at__isnull=True,
        student__deleted_at__isnull=False
    ).filter(on_personal_goals_on_school | on_group_goals_on_school)
    count = observations.count()
    observations.update(deleted_at=now)
    return count


def soft_delete_goals(school, now):
    # If student (i.e. this is a personal goal) AND student is soft-deleted -> mark as deleted
    # OR
    # If group (i.e. this is a group goal) AND group is soft-deleted -> mark as deleted
    goals = models.Goal.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(student_id__isnull=False, student__deleted_at__isnull=False) |
        Q(group_id__isnull=False, group__deleted_at__isnull=False, group__school=school)
    )
    count = goals.count()
    goals.update(deleted_at=now)
    return count


def soft_delete_user_groups(school, now, maintained_earlier_than):
    # IF Group is soft-deleted -> mark as deleted
    # OR
    # If UserGroup not maintained AND Group is valid -> mark as deleted
    # Note: This let's us keep memberships in out-dated (invalid) groups for historical purposes
    user_groups = models.UserGroup.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(group__deleted_at__isnull=False, group__school=school) |
        Q(
            group__in=models.Group.objects.within_validity_period(),
            maintained_at__lt=maintained_earlier_than,
            group__school=school
        )
    )
    count = user_groups.count()
    user_groups.update(deleted_at=now)
    return count


def hard_delete_groups(school, now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_GROUP days, hard delete
    groups = models.Group.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GROUP),
        school=school
    )
    # Note: This will cascade delete UserGroups
    count = groups.count()
    groups.delete()
    return count


def hard_delete_users(school, now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_USER days, hard delete
    # Note: This will cascade delete UserGroups, Personal Goals and Observations
    users = models.User.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_USER)
    )
    count = users.count()
    users.delete()
    return count


def hard_delete_observations(school, now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION days, hard delete
    on_personal_goals_on_school = Q(
        goal__student__isnull=False,
        goal__subject__owned_by_school=school
    )
    on_group_goals_on_school = Q(goal__group__school=school)

    observations = models.Observation.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION)
    ).filter(on_personal_goals_on_school | on_group_goals_on_school)
    count = observations.count()
    observations.delete()
    return count


def hard_delete_goals(school, now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_GOAL days, hard delete
    # Note: This will fail if there are Observations linked to the Goal
    goals = models.Goal.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GOAL)
    ).filter(
        Q(student_id__isnull=False, subject__owned_by_school=school) |
        Q(group_id__isnull=False, group__school=school)
    )
    count = goals.count()
    goals.delete()
    return count


def hard_delete_user_groups(school, now):
    # If deleted_at older than HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP hours, hard delete
    # Note: The short delay is to quickly update group memberships
    user_groups = models.UserGroup.objects.filter(
        deleted_at__lt=now - timezone.timedelta(hours=HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP),
        group__school=school
    )
    count = user_groups.count()
    user_groups.delete()
    return count
