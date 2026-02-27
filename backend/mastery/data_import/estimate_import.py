import os
import json
from urllib.parse import unquote
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
    incoming_groups_by_id = {group.get("id"): group for group in all_groups}
    # Single query fetching only feide_id instead of full objects
    existing_feide_ids = set(
        models.Group.objects.filter(school__org_number=org_number, deleted_at__isnull=True)
        .values_list('feide_id', flat=True)
    )
    for feide_id in existing_feide_ids:
        incoming_groups_by_id.pop(feide_id, None)
    return incoming_groups_by_id


def estimate_users_import(org_number):
    """Estimate which users will be added on import for ONE school from data_import/data/schools/<org>/users.json"""
    memberships_data = data_from_file(org_number, "memberships")
    incoming_users_by_id = {
        m["feide_id"]: m["name"]
        for members in memberships_data.values() for role in ("teachers", "students")
        for m in members.get(role, [])}

    # Single query fetching only feide_id instead of full User objects
    existing_feide_ids = set(
        models.User.objects.filter(
            user_groups__group__school__org_number=org_number, deleted_at__isnull=True
        ).values_list('feide_id', flat=True)
    )
    for feide_id in existing_feide_ids:
        incoming_users_by_id.pop(feide_id, None)
    return incoming_users_by_id


def estimate_memberships_import(org_number):
    """Estimate which memberships will be added on import for ONE school from data_import/data/schools/<org>/memberships.json"""
    memberships_data = data_from_file(org_number, "memberships")
    incoming_memberships = {}

    # Create lookup dict {feide_id: display_name} for all groups at school
    group_names = dict(
        models.Group.objects.filter(school__org_number=org_number, deleted_at__isnull=True)
        .values_list('feide_id', 'display_name')
    )

    for group_id, roles in memberships_data.items():
        group_name = group_names.get(group_id)
        for role in ("teacher", "student"):
            for membership in roles.get(f"{role}s", []):
                key = f"{group_id} // {role} // {membership['feide_id']}"
                incoming_memberships[key] = {
                    "group_id": group_id,
                    # fallback to part of feide_id if group not found in DB (i.e. the group itself is also new)
                    "group_name": group_name or unquote(group_id.split(':')[5]),
                    "role": role,
                    "feide_id": membership["feide_id"],
                    "user_name": membership["name"], }

    # Single query with select_related to avoid N+1 on group/role/user FK access
    existing_keys = set(
        models.UserGroup.objects.filter(
            group__school__org_number=org_number, deleted_at__isnull=True
        ).select_related('group', 'role', 'user')
        .values_list('group__feide_id', 'role__name', 'user__feide_id')
    )
    for group_feide_id, role_name, user_feide_id in existing_keys:
        key = f"{group_feide_id} // {role_name} // {user_feide_id}"
        incoming_memberships.pop(key, None)
    return incoming_memberships
