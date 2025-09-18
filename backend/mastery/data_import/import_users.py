import os
import json
from django.utils import timezone
from .helpers import does_file_exist
from mastery import models

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_memberships_from_file(org_number):
    """Import memberships for ONE school from data_import/data/schools/<org>/memeberships.json"""
    print("👉 import_memberships_from_file: BEGIN")

    # read memberships file
    if not does_file_exist(org_number, "memberships"):
        raise Exception(f"Memberships file not found for school {org_number}")

    memberships_file = os.path.join(data_dir, org_number, "memberships.json")
    with open(memberships_file, "r", encoding="utf-8") as file:
        memberships_data = json.load(file)

    teacher_role, student_role = ensure_roles_exist()

    # Progress reporting variables
    processed_count = 0
    users_created = 0
    users_maintained = 0
    users_failed = 0
    memberships_created = 0
    memberships_maintained = 0
    memberships_failed = 0
    chunk_size = 10
    errors = []
    processed_users = set()

    for feide_group_id, feide_group_memberships in memberships_data.items():
        group = models.Group.objects.filter(feide_id__exact=feide_group_id).first()
        if not group:
            errors.append({"error": "missing-group", "group_id": feide_group_id,
                          "message": f"Expected group not found: {feide_group_id}"})
            continue

        # Processing teachers and students in this group
        for role_key, role_obj in [("teachers", teacher_role), ("students", student_role)]:
            # Ensure user and membership for each member in this role
            for member_data in feide_group_memberships.get(role_key, []):
                user, user_was_created, user_error = ensure_user_exists(member_data)
                if user_error:
                    errors.append(
                        {"error": "ensure-user-failed", "feide_id": member_data.get("feide_id"),
                         "group_id": feide_group_id, "message": user_error})
                    users_failed += 1
                    continue

                # Only count user creation/maintain once per unique user
                user_id = user.feide_id
                if user_id not in processed_users:
                    processed_users.add(user_id)
                    if user_was_created:
                        users_created += 1
                    else:
                        users_maintained += 1

                # If we're here, user exists, now ensure membership
                _, membership_created, membership_error = ensure_membership_exists(user, group, role_obj)
                if membership_error:
                    errors.append(
                        {"error": "ensure-membership-failed", "feide_id": member_data.get("feide_id"),
                         "group_id": feide_group_id, "message": membership_error})
                    memberships_failed += 1
                elif membership_created:
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
                                    "failed": users_failed,
                                },
                                "membership": {
                                    "created": memberships_created,
                                    "maintained": memberships_maintained,
                                    "failed": memberships_failed,
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
                    "failed": users_failed,
                },
                "membership": {
                    "created": memberships_created,
                    "maintained": memberships_maintained,
                    "failed": memberships_failed,
                },
            },
            "errors": errors,
        },
        "is_done": True,
    }


def ensure_roles_exist():
    """Ensure that the roles 'teacher' and 'student' exist"""
    teacher_role = models.Role.objects.filter(name="teacher").first()
    student_role = models.Role.objects.filter(name="student").first()

    if not teacher_role:
        teacher_role = models.Role.objects.create(
            name="teacher", maintained_at=timezone.now()
        )

    if not student_role:
        student_role = models.Role.objects.create(
            name="student", maintained_at=timezone.now()
        )

    return teacher_role, student_role


def ensure_user_exists(user_data):
    """
    Ensure a user exists, maintaining it if it already exists or creating it if not.
    Returns (user, created_bool, error_message) 
    """
    try:
        user = models.User.objects.filter(feide_id__exact=user_data["feide_id"]).first()

        if user:
            user.name = user_data.get("name", user.name)
            user.email = user_data.get("email", user.email)
            user.maintained_at = timezone.now()
            user.save()
            print(f"User maintained: {user.email}")
            return user, False, None

        user = models.User.objects.create(
            feide_id=user_data["feide_id"],
            name=user_data.get("name", ""),
            email=user_data.get("email", ""),
            maintained_at=timezone.now(),
        )
        print(f"User created: {user.email}")
        return user, True, None

    except Exception as error:
        error_message = f"Ensure user failed {user_data.get('feide_id', '??')}: {str(error)[:1000]}"
        return None, False, error_message


def ensure_membership_exists(user, group, role):
    """
    Ensure membership exists for user in group with role, create if not existing or maintain if existing
    Returns (membership, created_bool, error_message)
    """
    try:
        # Check if membership exists for this user
        existing_membership = models.UserGroup.objects.filter(
            user=user, group=group
        ).first()

        if existing_membership:
            existing_membership.role = role
            existing_membership.maintained_at = timezone.now()
            existing_membership.save()
            print(f"Membership maintained: {user.email} in {group.display_name} as {role.name}")
            return existing_membership, False, None

        # Create new membership
        new_membership = models.UserGroup.objects.create(
            user=user, group=group, role=role, maintained_at=timezone.now()
        )
        print(f"Membership created: {user.email} in {group.display_name} as {role.name}")
        return new_membership, True, None

    except Exception as error:
        error_message = f"Ensure membership failed for user {user.email}: {str(error)[:1000]}"
        return None, False, error_message
