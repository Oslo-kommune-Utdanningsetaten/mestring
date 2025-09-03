import os
import json
from django.utils import timezone
from mastery import models

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_users_from_file(
    org_number, is_overwrite_enabled=False
):
    """Import users for ONE school from imports/data/schools/<org>/users.json"""
    print("👉 import_users_from_file: BEGIN")

    users_file = os.path.join(data_dir, org_number, "users.json")
    if not os.path.exists(users_file):
        raise Exception(
            f"Users file not found for school {org_number}. Fetch users first."
        )

    with open(users_file, "r") as file:
        memberships = json.load(file)

    if not isinstance(memberships, dict):
        raise Exception(
            "Invalid users file format: expected a mapping of groupId -> {teachers/students/other}"
        )

    result = import_users_from_data(
        memberships,
        is_overwrite_enabled=is_overwrite_enabled,
    )

    print("✅ import_users_from_file COMPLETED")
    return result


def import_users_from_data(
    memberships_data, is_overwrite_enabled=False
):
    """Import users and their memberships from provided data"""
    teacher_role, student_role = ensure_roles_exist()

    stats = {
        "users_created": 0,
        "users_existing": 0,
        "users_updated": 0,
        "memberships_created": 0,
        "memberships_existing": 0,
        "groups_processed": len(memberships_data),
        "groups_not_found": 0,
    }

    # Track unique users
    created_users = set()
    existing_users = set()
    updated_users = set()

    for group_feide_id, feide_group_memberships in memberships_data.items():
        group = models.Group.objects.filter(feide_id__exact=group_feide_id).first()
        if not group:
            stats["groups_not_found"] += 1
            continue

        # Process teachers
        for teacher in feide_group_memberships.get("teachers", []):
            user, user_created, user_updated = ensure_user_exists(
                teacher,
                is_overwrite_enabled=is_overwrite_enabled,
            )
            if user_created:
                created_users.add(user.feide_id)
            elif user_updated:
                updated_users.add(user.feide_id)
            else:
                existing_users.add(user.feide_id)

            membership_created = ensure_membership(
                user, group, teacher_role
            )
            if membership_created:
                stats["memberships_created"] += 1
            else:
                stats["memberships_existing"] += 1

        # Process students
        for student in feide_group_memberships.get("students", []):
            user, user_created, user_updated = ensure_user_exists(
                student,
                is_overwrite_enabled=is_overwrite_enabled,
            )
            if user_created:
                created_users.add(user.feide_id)
            elif user_updated:
                updated_users.add(user.feide_id)
            else:
                existing_users.add(user.feide_id)

            membership_created = ensure_membership(
                user, group, student_role
            )
            if membership_created:
                stats["memberships_created"] += 1
            else:
                stats["memberships_existing"] += 1

    # Set correct counts
    stats["users_created"] = len(created_users)
    stats["users_existing"] = len(existing_users)
    stats["users_updated"] = len(updated_users)

    return {"message": "Users imported successfully", "statistics": stats}


def ensure_roles_exist():
    """Ensure that the roles 'teacher' and 'student' exist. In dry run: don't write."""
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


def ensure_user_exists(user_data, is_overwrite_enabled=False):
    """Ensure user exists in database, create if not (skip writes in dry run)."""
    user = models.User.objects.filter(feide_id__exact=user_data["feide_id"]).first()
    if user:
        if is_overwrite_enabled:
            user.name = user_data["name"]
            user.email = user_data["email"]
            user.maintained_at = timezone.now()

            user.save()
            print(f"  🔄 User updated: {user.email}")
            return user, False, True  # updated
        else:
            print(f"  📋 User already exists: {user.email}")
            return user, False, False
    else:
        user = models.User.objects.create(
            name=user_data["name"],
            feide_id=user_data["feide_id"],
            email=user_data["email"],
            maintained_at=timezone.now(),
        )
        print(f"  ✅ User created: {user.email}")
        return user, True, False


def ensure_membership(user, group, role):
    """Ensure user is member of group with role; skip write in dry run."""

    user_group, created = models.UserGroup.objects.get_or_create(
        user=user, group=group, role=role, defaults={"maintained_at": timezone.now()}
    )
    if created:
        print(f"    ✅ Membership created: {user.email} -> {group.display_name}")
        return True
    else:
        print(f"    📋 Membership exists: {user.email} -> {group.display_name}")
        return False
