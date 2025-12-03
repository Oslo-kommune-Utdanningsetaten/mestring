from django.utils import timezone
from mastery import models
from django.db.models import Q, Count
import logging
logger = logging.getLogger(__name__)


def update_data_integrity(maintenance_threshold):

    changes = {}
    errors = []
    now = timezone.now()
    logger.debug(f"Everything maintained earlier than %s will be soft-deleted", maintenance_threshold)

    # Soft delete
    changes["group"] = {}
    changes["group"]["soft-deleted"] = soft_delete_groups(now, maintenance_threshold)

    changes["user"] = {}
    changes["user"]["soft-deleted"] = soft_delete_users(now, maintenance_threshold)
    # Observation: if student not maintained since maintenance_threshold, mark as deleted
    # Goal: if student and student not maintained since maintenance_threshold, mark as deleted
    # Goal: if Group and Group not maintained since maintenance_threshold, mark as deleted
    # UserGroup: if UserGroup not maintained since maintenance_threshold AND Group is valid, mark as deleted (DO NOT mess with memberships to invalid groups)
    #
    # Hard delete
    # Groups: if deleted_at older than 90 days, hard delete
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
    # if not maintained since maintenance_threshold AND not deleted AND group is valid -> mark as deleted (DO NOT mess with invalid groups)
    groups = models.Group.objects.filter(
        deleted_at__isnull=True, maintained_at__lt=maintenance_threshold).within_validity_period()
    count = groups.count()
    groups.update(deleted_at=now)
    return count


def soft_delete_users(now, maintenance_threshold):
    # if not superadmin AND not maintained since maintenance_threshold AND no non-deleted UserGroups -> mark as deleted
    users = models.User.objects.annotate(
        active_user_groups_count=Count(
            'user_groups', filter=Q(user_groups__deleted_at__isnull=True))
    ).filter(
        is_superadmin=False,
        maintained_at__lt=maintenance_threshold,
        active_user_groups_count=0
    )
    count = users.count()
    users.update(deleted_at=now)
    return count
