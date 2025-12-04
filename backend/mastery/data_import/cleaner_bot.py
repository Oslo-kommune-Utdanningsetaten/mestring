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
def update_data_integrity(maintained_earlier_than):
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
    logger.debug(f"Begin soft-delete of anything maintained earlier than %s", maintained_earlier_than)
    changes["group"]["soft-deleted"] = soft_delete_groups(now, maintained_earlier_than)
    changes["user"]["soft-deleted"] = soft_delete_users(now, maintained_earlier_than)
    changes["observation"]["soft-deleted"] = soft_delete_observations(now, maintained_earlier_than)
    changes["goal"]["soft-deleted"] = soft_delete_goals(now, maintained_earlier_than)
    changes["user_group"]["soft-deleted"] = soft_delete_user_groups(now, maintained_earlier_than)
    logger.debug(f"End soft-delete")

    # Hard delete
    logger.debug(f"Begin hard-delete of anything soft-deleted a sufficiently long time ago")
    changes["group"]["hard-deleted"] = hard_delete_groups(now)
    changes["user"]["hard-deleted"] = hard_delete_users(now)
    changes["observation"]["hard-deleted"] = hard_delete_observations(now)
    changes["goal"]["hard-deleted"] = hard_delete_goals(now)
    changes["user_group"]["hard-deleted"] = hard_delete_user_groups(now)
    logger.debug(f"End hard-delete")

    yield {
        "result": {
            "entity": "school",
            "action": "update_data_integrity",
            "errors": errors,
            "changes": changes,
        },
        "is_done": True,
    }


def soft_delete_groups(now, maintained_earlier_than):
    # If not maintained since maintained_earlier_than AND not deleted AND group is valid -> mark as deleted
    # Note: DO NOT mess with invalid groups
    groups = models.Group.objects.filter(
        deleted_at__isnull=True,
        maintained_at__lt=maintained_earlier_than
    ).within_validity_period()
    count = groups.count()
    groups.update(deleted_at=now)
    return count


def soft_delete_users(now, maintained_earlier_than):
    # If not superadmin AND not maintained since maintained_earlier_than AND no non-deleted UserGroups -> mark as deleted
    users = models.User.objects.annotate(
        active_user_groups_count=Count('user_groups',
                                       filter=Q(user_groups__deleted_at__isnull=True))
    ).filter(
        deleted_at__isnull=True,
        is_superadmin=False,
        maintained_at__lt=maintained_earlier_than,
        active_user_groups_count=0
    )
    count = users.count()
    users.update(deleted_at=now)
    return count


def soft_delete_observations(now, maintained_earlier_than):
    # If student is soft-deleted -> mark as deleted
    observations = models.Observation.objects.filter(
        deleted_at__isnull=True,
        student__deleted_at__isnull=False
    )
    count = observations.count()
    observations.update(deleted_at=now)
    return count


def soft_delete_goals(now, maintained_earlier_than):
    # If student (i.e. this is a personal goal) AND student is soft-deleted -> mark as deleted
    # OR
    # If group (i.e. this is a group goal) AND group is soft-deleted -> mark as deleted
    goals = models.Goal.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(student_id__isnull=False, student__deleted_at__isnull=False) |
        Q(group_id__isnull=False, group__deleted_at__isnull=False)
    )
    count = goals.count()
    goals.update(deleted_at=now)
    return count


def soft_delete_user_groups(now, maintained_earlier_than):
    # If UserGroup not maintained since maintained_earlier_than AND Group is valid -> mark as deleted
    # Note: This let's us keep memberships in out-dated (invalid) groups for historical purposes
    # OR
    # IF Group is soft-deleted -> mark as deleted
    user_groups = models.UserGroup.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(group__in=models.Group.objects.within_validity_period(),
          maintained_at__lt=maintained_earlier_than) |
        Q(group__deleted_at__isnull=False)
    )
    count = user_groups.count()
    user_groups.update(deleted_at=now)
    return count


def hard_delete_groups(now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_GROUP days, hard delete
    groups = models.Group.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GROUP)
    )
    # Note: This will cascade delete UserGroups
    count = groups.count()
    groups.delete()
    return count


def hard_delete_users(now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_USER days, hard delete
    # Note: This will cascade delete UserGroups, Personal Goals and Observations
    users = models.User.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_USER)
    )
    count = users.count()
    users.delete()
    return count


def hard_delete_observations(now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION days, hard delete
    observations = models.Observation.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_OBSERVATION)
    )
    count = observations.count()
    observations.delete()
    return count


def hard_delete_goals(now):
    # If deleted_at older than DAYS_BEFORE_HARD_DELETE_OF_GOAL days, hard delete
    # Note: This will fail if there are Observations linked to the Goal
    goals = models.Goal.objects.filter(
        deleted_at__lt=now - timezone.timedelta(days=DAYS_BEFORE_HARD_DELETE_OF_GOAL)
    )
    count = goals.count()
    goals.delete()
    return count


def hard_delete_user_groups(now):
    # If deleted_at older than HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP hours, hard delete
    # Note: The short delay is to quickly update group memberships
    user_groups = models.UserGroup.objects.filter(
        deleted_at__lt=now - timezone.timedelta(hours=HOURS_BEFORE_HARD_DELETE_OF_USER_GROUP)
    )
    count = user_groups.count()
    user_groups.delete()
    return count
