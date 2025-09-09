import os
import json
from django.utils import timezone
from .helpers import does_file_exist
from mastery import models

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_users_from_file(
    org_number, is_overwrite_enabled=False, is_crash_on_error_enabled=False
):
    """Import users for ONE school from imports/data/schools/<org>/users.json"""
    print("👉 import_users_from_file: BEGIN")

    if not does_file_exist(org_number, "users"):
        raise Exception(
            f"Users file not found for school {org_number}. Fetch users first."
        )

    users_file = os.path.join(data_dir, org_number, "users.json")
    with open(users_file, "r") as file:
        memberships = json.load(file)

    if not isinstance(memberships, dict):
        raise Exception(
            "Invalid users file format: expected a mapping of groupId -> {teachers/students/other}"
        )

    result = process_user_and_membership_data(
        memberships,
        is_overwrite_enabled=is_overwrite_enabled,
        is_crash_on_error_enabled=is_crash_on_error_enabled,
    )

    print("✅ import_users_from_file COMPLETED")
    return result


def process_user_and_membership_data(
    memberships_data, is_overwrite_enabled=False, is_crash_on_error_enabled=False
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
        "errors": [],
    }

    # Track unique users
    created_users = set()
    existing_users = set()
    updated_users = set()

    for feide_group_id, feide_group_memberships in memberships_data.items():
        group = models.Group.objects.filter(feide_id__exact=feide_group_id).first()
        if not group:
            stats["groups_not_found"] += 1
            error_msg = f"Group not found: {feide_group_id}"
            stats["errors"].append({"name": feide_group_id, "message": error_msg})
            print(f"  ⚠️ {error_msg}")
            if is_crash_on_error_enabled:
                raise Exception(f"Import stopped: {error_msg}")
            continue

        # Process teachers
        for teacher in feide_group_memberships.get("teachers", []):
            user, user_created, user_updated, user_error = ensure_user_exists(
                teacher,
                is_overwrite_enabled=is_overwrite_enabled,
            )

            if user_error:
                stats["errors"].append({
                    "name": teacher.get("name", "Unknown teacher"),
                    "message": user_error
                })
                if is_crash_on_error_enabled:
                    raise Exception(f"Import stopped: {user_error}")
                continue

            if user_created:
                created_users.add(user.feide_id)
            elif user_updated:
                updated_users.add(user.feide_id)
            else:
                existing_users.add(user.feide_id)

            membership_created, membership_error = ensure_membership(
                user, group, teacher_role
            )

            if membership_error:
                stats["errors"].append({
                    "name": f"{user.feide_id} ---> {group.display_name}",
                    "message": membership_error
                })
                print(f"  ❌ {membership_error}")
                if is_crash_on_error_enabled:
                    raise Exception(f"Import stopped: {membership_error}")
                continue

            if membership_created:
                stats["memberships_created"] += 1
            else:
                stats["memberships_existing"] += 1

        # Process students
        for student in feide_group_memberships.get("students", []):
            user, user_created, user_updated, user_error = ensure_user_exists(
                student,
                is_overwrite_enabled=is_overwrite_enabled,
            )
            if user_error:
                stats["errors"].append({
                    "name": student.get("name", "Unknown student"),
                    "message": user_error
                })
                if is_crash_on_error_enabled:
                    raise Exception(f"Import stopped: {user_error}")
                continue

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


def ensure_user_exists(user_data, is_overwrite_enabled=False, is_crash_on_error_enabled=False):
    """Ensure user exists in database, create if not"""
    try:
        user = models.User.objects.filter(feide_id__exact=user_data["feide_id"]).first()

        if user and is_overwrite_enabled:
            user.name = user_data.get("name", user.name)
            user.email = user_data.get("email", user.email)
            user.maintained_at = timezone.now()
            user.save()
            print(f"  🔄 User updated: {user.email}")
            return user, False, True, None
        
        if user:
            print(f"  📋 User exists: {user.email}")
            return user, False, False, None
        
        user = models.User.objects.create(
            feide_id=user_data["feide_id"],
            name=user_data.get("name", ""),
            email=user_data.get("email", ""),
            maintained_at=timezone.now(),
        )
        print(f"  ✅ User created: {user.email}")
        return user, True, False, None
    
    except Exception as e:
        error_messasge = f"Error processing user {user_data.get('feide_id', 'unknown')}: {str(e)}"
        print(f"  ❌ {error_messasge}")
        return None, False, False, error_messasge



def ensure_membership(user, group, role):
    """Ensure user is member of group with role"""
    try:
        user_group, created = models.UserGroup.objects.get_or_create(
            user=user, group=group, role=role, defaults={"maintained_at": timezone.now()}
        )
        if created:
            print(f"    ✅ Membership created: {user.email} -> {group.display_name}")
            return True, None  
        else:
            print(f"    📋 Membership exists: {user.email} -> {group.display_name}")
            return False, None  
            
    except Exception as e:
        error_message = f"Failed to create membership for {user.email}: {str(e)}"
        print(f"    ❌ {error_message}")
        return False, error_message
