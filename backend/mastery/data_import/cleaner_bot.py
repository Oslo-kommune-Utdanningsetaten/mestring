from django.utils import timezone
from mastery import models
import logging
logger = logging.getLogger(__name__)


def update_data_integrity(org_number, maintenance_threshold):
    logger.debug("Update data for", org_number)
    school = models.School.objects.filter(org_number=org_number).first()
    if not school:
        message = "School with org number {org_number} not found"
        logger.error(message)
        raise Exception(message)

    changes = {}
    errors = []
    now = timezone.now()

    logger.debug("Everything maintained earlier than", maintenance_threshold, "will be soft-deleted")
    print("Everything maintained earlier than", maintenance_threshold, "will be soft-deleted")

    # Soft delete
    # Groups: if not maintained since maintenance_threshold AND group is valid, mark as deleted (DO NOT mess with invalid groups)
    changes["groups"] = {}
    groups = models.Group.objects.filter(
        school=school, deleted_at__isnull=True, maintained_at__lt=maintenance_threshold).within_validity_period()
    print("🦊Soft-deleting", groups.count(), "groups")
    changes["groups"]["soft-deleted"] = groups.count()
    groups.update(deleted_at=now)
    # User: if not superadmin, or no non-deleted UserGroup memberships, mark as deleted
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
    #     "groups": {
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
