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


def data_from_file(org_number, data_type):
    """Reads data (groups or memberships) for ONE school from data_import/data/schools/<org>/<data_type>.json"""

    # read file
    if not does_file_exist(org_number, data_type):
        message = f"Fetched data ({data_type}) file not found for school {org_number}"
        logger.error(message)
        raise Exception(message)

    data_file = os.path.join(data_dir, org_number, f"{data_type}.json")
    with open(data_file, "r", encoding="utf-8") as file:
        return json.load(file)


def estimate_groups_import(org_number):
    """Estimate which groups will be added on import for ONE school from data_import/data/schools/<org>/groups.json"""
    groups_data = data_from_file(org_number, "groups")
    # groups.json is a dict with keys: owners, schools, teaching, basis, subjects
    # Flatten basis + teaching groups (the ones that become Group model rows)
    all_groups = groups_data.get("basis", []) + groups_data.get("teaching", [])
    incoming_groups_by_id = {}
    for group in all_groups:
        incoming_groups_by_id[group.get("id")] = group
    current_groups = models.Group.objects.filter(school__org_number=org_number, deleted_at__isnull=True)
    for group in current_groups:
        if group.feide_id in incoming_groups_by_id:
            del incoming_groups_by_id[group.feide_id]
    return incoming_groups_by_id


def estimate_users_import(org_number):
    """Estimate which users will be added on import for ONE school from data_import/data/schools/<org>/users.json"""
    memberships_data = data_from_file(org_number, "memberships")
    incoming_users_by_id = {
        m["feide_id"]: m["name"]
        for members in memberships_data.values() for role in ("teachers", "students")
        for m in members.get(role, [])}

    current_users = models.User.objects.filter(
        user_groups__group__school__org_number=org_number, deleted_at__isnull=True).distinct()
    # return a dict (key: feide_id, value: user_data) of incoming users that are not in our database yet
    for user in current_users:
        if user.feide_id in incoming_users_by_id:
            del incoming_users_by_id[user.feide_id]
    return incoming_users_by_id


def estimate_memberships_import(org_number):
    """Estimate which memberships will be added on import for ONE school from data_import/data/schools/<org>/memberships.json"""
    memberships_data = data_from_file(org_number, "memberships")
    incoming_memberships = {}

    for group_id, roles in memberships_data.items():
        for role in ("teacher", "student"):
            for membership in roles.get(f"{role}s", []):
                key = f"{group_id} // {role} // {membership['feide_id']}"
                incoming_memberships[key] = {
                    "group_id": group_id, "group_name": models.Group.objects.filter(
                        feide_id=group_id, school__org_number=org_number).first().display_name,
                    "role": role,
                    "feide_id": membership["feide_id"],
                    "user_name": membership["name"], }
    current_user_groups = models.UserGroup.objects.filter(
        group__school__org_number=org_number, deleted_at__isnull=True)
    for user_group in current_user_groups:
        key = f"{user_group.group.feide_id} // {user_group.role.name} // {user_group.user.feide_id}"
        if key in incoming_memberships:
            del incoming_memberships[key]
    return incoming_memberships
