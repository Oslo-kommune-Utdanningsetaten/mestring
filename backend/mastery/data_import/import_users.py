import os
import json
from django.utils import timezone
from .helpers import does_file_exist
from mastery import models

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")


def import_memberships_from_file(org_number):
    """Import memberships for ONE school from imports/data/schools/<org>/users.json"""
    print("👉 import_memberships_from_file: BEGIN")

    # read memberships file
    if not does_file_exist(org_number, "memberships"):
        raise Exception(f"Memberships file not found for school {org_number}")
    memberships_file = os.path.join(data_dir, org_number, "memberships.json")
    with open(memberships_file, "r") as file:
        memberships_data = json.load(file)

    teacher_role, student_role = ensure_roles_exist()

    # count all memberships to process
    total_teachers = sum(len(group.get("teachers", [])) for group in memberships_data.values())
    total_students = sum(len(group.get("students", [])) for group in memberships_data.values())
    total_memberships = total_teachers + total_students
    errors = []
    memberships_successfully_handled = 0

    for feide_group_id, feide_group_memberships in memberships_data.items():
        group = models.Group.objects.filter(feide_id__exact=feide_group_id).first()
        if not group:
            message = f"Expected group not found: {feide_group_id}"
            errors.append({"error": "missing-group", "message": message})
            continue

        # Processing teachers and students in this group
        for role_key, role_obj in [("teachers", teacher_role), ("students", student_role)]:
            # Ensure user and membership for each member in this role
            for member_data in feide_group_memberships.get(role_key, []):
                user, _, _, error = ensure_user_exists(member_data)
                if error:
                    message = f"Problem ensuring {role_key}: {member_data['feide_id']}. {error}"
                    errors.append({"error": "user-ensure-error", "message": message})
                    continue
                # If we're here, user exists, now ensure membership
                _, error = ensure_membership_exists(user, group, role_obj)
                if error:
                    message = f"Problem ensuring membership: {feide_group_id}. {error}"
                    errors.append({"error": "membership-ensure-error", "message": message})
                    continue
                memberships_successfully_handled += 1

        # report progress for each group
        yield {
            "result": {
                "entity": "user",
                "action": "import",
                "total_count": total_memberships,
                "success_count": memberships_successfully_handled,
                "failure_count": len(errors),
                "errors": errors,
            },
            "is_done": False,
        }

    yield {
        "result": {
            "entity": "user",
            "action": "import",
            "total_count": total_memberships,
            "failure_count": len(errors),
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
    """Ensure user exists in database, create if not"""
    try:
        user = models.User.objects.filter(feide_id__exact=user_data["feide_id"]).first()

        if user:
            user.name = user_data.get("name", user.name)
            user.email = user_data.get("email", user.email)
            user.maintained_at = timezone.now()
            user.save()
            print(f"User updated: {user.email}")
            return user, False, True, None

        user = models.User.objects.create(
            feide_id=user_data["feide_id"],
            name=user_data.get("name", ""),
            email=user_data.get("email", ""),
            maintained_at=timezone.now(),
        )
        print(f"User created: {user.email}")
        return user, True, False, None

    except Exception as error:
        error_message = f"Ensure user failed {user_data.get('feide_id', '??')}: {str(error)[:1000]}"
        return None, False, False, error_message


def ensure_membership_exists(user, group, role):
    """Ensure user is member of group with role"""
    try:
        user_group, created = models.UserGroup.objects.get_or_create(
            user=user, group=group, role=role, defaults={"maintained_at": timezone.now()}
        )
        print(f"Membership {'created' if created else 'exists'}: {user.email} -> {group.display_name}")
        return user_group, None

    except Exception as error:
        error_message = f"Failed to create membership for {user.email}: {str(error)[:1000]}"
        return None, error_message
