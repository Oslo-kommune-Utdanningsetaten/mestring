from django.utils import timezone
from mastery import models
from django.db.models import Q, Count
import logging
logger = logging.getLogger(__name__)


def update_data_integrity(maintenance_threshold):
    changes = {
        "group": {},
        "user": {},
        "observation": {},
        "goal": {},
        "user_group": {},
    }
    errors = []
    now = timezone.now()
    logger.debug(f"Everything maintained earlier than %s will be soft-deleted", maintenance_threshold)

    # Soft delete
    changes["group"]["soft-deleted"] = soft_delete_groups(now, maintenance_threshold)
    changes["user"]["soft-deleted"] = soft_delete_users(now, maintenance_threshold)
    changes["observation"]["soft-deleted"] = soft_delete_observations(now, maintenance_threshold)
    changes["goal"]["soft-deleted"] = soft_delete_goals(now, maintenance_threshold)
    changes["user_group"]["soft-deleted"] = soft_delete_user_groups(now, maintenance_threshold)

    # Hard delete
    # Groups: if deleted_at older than 90 days, hard delete
    # changes["group"]["hard-deleted"] = hard_delete_groups(now)
    # User: if deleted_at older than 90 days, hard delete
    # Observation: if deleted_at older than 90 days, hard delete
    # Goal: if deleted_at older than 90 days, hard delete
    # UserGroup: if deleted_at older than 1 hour, hard delete
    #
    # Output progress chunks as:
    # "changes": {
    #     "group": {
    #         "soft-deleted": 0,
    #         "hard-deleted": 0,
    #     },
    #     "...": {}
    # },

    yield {
        "result": {
            "entity": "school",
            "action": "update_data_integrity",
            "errors": errors,
            "changes": changes,
        },
        "is_done": True,
    }


def soft_delete_groups(now, maintenance_threshold):
    # If not maintained since maintenance_threshold AND not deleted AND group is valid -> mark as deleted
    # Note: DO NOT mess with invalid groups
    groups = models.Group.objects.filter(
        deleted_at__isnull=True,
        maintained_at__lt=maintenance_threshold
    ).within_validity_period()
    count = groups.count()
    groups.update(deleted_at=now)
    return count


def soft_delete_users(now, maintenance_threshold):
    # If not superadmin AND not maintained since maintenance_threshold AND no non-deleted UserGroups -> mark as deleted
    users = models.User.objects.annotate(
        active_user_groups_count=Count('user_groups',
                                       filter=Q(user_groups__deleted_at__isnull=True))
    ).filter(
        deleted_at__isnull=True,
        is_superadmin=False,
        maintained_at__lt=maintenance_threshold,
        active_user_groups_count=0
    )
    count = users.count()
    users.update(deleted_at=now)
    return count


def soft_delete_observations(now, maintenance_threshold):
    # If student is soft-deleted -> mark as deleted
    observations = models.Observation.objects.filter(
        deleted_at__isnull=True,
        student__deleted_at__isnull=False
    )
    count = observations.count()
    observations.update(deleted_at=now)
    return count


def soft_delete_goals(now, maintenance_threshold):
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


def soft_delete_user_groups(now, maintenance_threshold):
    # If UserGroup not maintained since maintenance_threshold AND Group is valid -> mark as deleted
    # Note: This let's us keep memberships in out-dated (invalid) groups for historical purposes
    # OR
    # IF Group is soft-deleted -> mark as deleted
    user_groups = models.UserGroup.objects.filter(
        deleted_at__isnull=True
    ).filter(
        Q(group__in=models.Group.objects.within_validity_period(),
          maintained_at__lt=maintenance_threshold) |
        Q(group__deleted_at__isnull=False)
    )
    count = user_groups.count()
    user_groups.update(deleted_at=now)
    return count


def hard_delete_groups(now):
    return 0
