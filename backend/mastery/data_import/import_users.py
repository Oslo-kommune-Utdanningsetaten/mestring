import os
import json
from django.utils import timezone
from .helpers import does_file_exist
from mastery import models
import logging

logger = logging.getLogger(__name__)

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_memberships_from_file(org_number):
    """Import memberships for ONE school from data_import/data/schools/<org>/memeberships.json"""
    logger.debug("Starting membership import for organization: %s", org_number)

    # read memberships file
    if not does_file_exist(org_number, "memberships"):
        logger.error("Memberships file not found for school %s", org_number)
        raise Exception(f"Memberships file not found for school {org_number}")

    memberships_file = os.path.join(data_dir, org_number, "memberships.json")
    with open(memberships_file, "r", encoding="utf-8") as file:
        memberships_data = json.load(file)
    yield from import_memberships(memberships_data)


def import_memberships(memberships_data):
    """Import memberships from provided data structure"""
    teacher_role, student_role, _, _, _ = ensure_roles_exist()

    # Progress reporting variables
    processed_count = 0
    users_created = 0
    users_maintained = 0
    memberships_created = 0
    memberships_maintained = 0
    chunk_size = 10
    errors = []
    processed_users = set()

    for feide_group_id, feide_group_memberships in memberships_data.items():
        group = models.Group.objects.filter(feide_id__exact=feide_group_id).first()
        if not group:
            logger.warning("Expected group not found: %s", feide_group_id)
            errors.append({"error": "missing-group", "group_id": feide_group_id,
                          "message": f"Expected group not found: {feide_group_id}"})
            continue

        # Processing teachers and students in this group
        for role_key, role_obj in [("teachers", teacher_role), ("students", student_role)]:
            # Ensure user and membership for each member in this role
            for member_data in feide_group_memberships.get(role_key, []):

                user, user_was_created = ensure_user_exists(member_data)

                # Only count user creation/maintain once per unique user
                user_id = user.feide_id
                if user_id not in processed_users:
                    processed_users.add(user_id)
                    if user_was_created:
                        users_created += 1
                    else:
                        users_maintained += 1

                # If we're here, user exists, now ensure membership
                _, membership_created = ensure_membership_exists(user, group, role_obj)

                if membership_created:
                    memberships_created += 1
                else:
                    memberships_maintained += 1

                processed_count += 1

                # Report progress every chunk_size operations
                if processed_count % chunk_size == 0:
                    yield {
                        "result": {
                            "entity": "user",
                            "action": "import",
                            "changes": {
                                "user": {
                                    "created": users_created,
                                    "maintained": users_maintained,
                                },
                                "membership": {
                                    "created": memberships_created,
                                    "maintained": memberships_maintained,
                                },
                            },
                            "errors": errors,
                        },
                        "is_done": False,
                    }

    yield {
        "result": {
            "entity": "user",
            "action": "import",
            "changes": {
                "user": {
                    "created": users_created,
                    "maintained": users_maintained,
                },
                "membership": {
                    "created": memberships_created,
                    "maintained": memberships_maintained,
                },
            },
            "errors": errors,
        },
        "is_done": True,
    }


def ensure_roles_exist():
    """Ensure necessary roles exist"""
    role_names = ["teacher", "student", "admin", "staff", "inspector"]
    roles = []

    for role_name in role_names:
        role, _ = models.Role.objects.get_or_create(
            name=role_name,
            defaults={"maintained_at": timezone.now()}
        )
        roles.append(role)

    return tuple(roles)


def ensure_user_exists(user_data):
    """
    Ensure a user exists, maintaining it if it already exists or creating it if not.
    Returns (user, created_bool)
    """
    user = models.User.objects.filter(feide_id__exact=user_data["feide_id"]).first()
    now = timezone.now()
    if user:
        user.name = user_data.get("name", user.name)
        user.email = user_data.get("email", user.email)
        user.maintained_at = now
        if user.deleted_at:
            user.deleted_at = None
            # Cascade un-delete related objects
            models.Observation.objects.filter(student=user).update(
                deleted_at=None, maintained_at=now)
            models.Goal.objects.filter(student=user).update(deleted_at=None, maintained_at=now)
        logger.debug("User maintained: %s", user.email)
        user.save()
        return user, False

    user = models.User.objects.create(
        feide_id=user_data["feide_id"],
        name=user_data.get("name", None),
        email=user_data.get("email", None),
        maintained_at=now,
    )
    logger.debug("User created: %s", user.email)
    return user, True


def ensure_membership_exists(user, group, role):
    """
    Ensure membership exists for user in group with role, create if not existing or maintain if existing
    Returns (membership, created_bool)
    """

    # Check if membership exists for this user
    existing_membership = models.UserGroup.objects.filter(
        user=user, group=group, role=role
    ).first()

    if existing_membership:
        existing_membership.maintained_at = timezone.now()
        existing_membership.deleted_at = None  # Unset, in case it was set
        existing_membership.save(update_fields=['maintained_at', 'deleted_at'])
        logger.debug("Membership maintained: %s in %s as %s", user.email, group.display_name, role.name)
        return existing_membership, False

    # Create new membership
    new_membership = models.UserGroup.objects.create(
        user=user, group=group, role=role, maintained_at=timezone.now()
    )
    logger.debug("Membership created: %s in %s as %s", user.email, group.display_name, role.name)
    return new_membership, True
