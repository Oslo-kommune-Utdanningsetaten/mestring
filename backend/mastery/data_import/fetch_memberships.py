import os
import json
import requests
from .helpers import create_user_item, get_feide_access_token
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

# API Configuration
MEMEBERS_URL = os.environ.get('MEMEBERS_URL')

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')


def fetch_memberships_from_feide(org_number: str, anonymize=False):
    """Fetch memberships for one school by reading its groups.json and hitting Feide members API."""
    logger.debug("Starting membership fetch for organization: %s", org_number)
    token = get_feide_access_token()

    # Ensure per-school groups file exists
    school_dir = os.path.join(data_dir, org_number)
    groups_file = os.path.join(school_dir, 'groups.json')
    if not os.path.exists(groups_file):
        logger.error("Groups file not found for school %s at path: %s", org_number, groups_file)
        raise Exception(f"Groups file not found for school {org_number}. Fetch groups first.")

    # Load per-school groups
    with open(groups_file, 'r', encoding="utf-8") as f:
        groups_data = json.load(f)

    # Collect group ids (basis + teaching are what we care about for memberships)
    basis_groups = groups_data.get('basis', [])
    teaching_groups = groups_data.get('teaching', [])
    all_groups = basis_groups + teaching_groups

    memberships = {}
    errors = []
    total_memberships = 0
    total_teacher_memberships = 0
    total_student_memberships = 0
    unique_users = set()

    # Progress tracking
    total_group_count = len(all_groups)

    for index, group in enumerate(all_groups):
        group_id = group.get('id')
        if not group_id:
            group_name = group.get('displayName', 'unknown')
            logger.warning("Group without ID found: %s", group_name)
            errors.append({"error": "data-error", "message": f"Group without id {group_name}"})
            continue

        logger.debug("Processing group %d/%d: %s", index + 1, total_group_count, group_id)

        # Percent-encode the full Feide id when placing in the URL path
        group_members_url = f"{MEMEBERS_URL}/{quote(group_id, safe='')}/members"
        # Fetch members for this group
        members_response = requests.get(group_members_url, headers={"Authorization": "Bearer " + token})

        if members_response.status_code != 200:
            logger.error("Failed to fetch members for group %s: HTTP %d",
                         group_id, members_response.status_code)
            errors.append({"error": "fetch-error", "message": f"Failed to fetch members for group {group_id}"})
            raise Exception(
                f"Failed to fetch members for group {group_id}: HTTP {members_response.status_code}")

        memberships[group_id] = {"teachers": [], "students": [], "other": []}
        feide_group_members = members_response.json() or []

        # Track memberships by role

        for feide_member in feide_group_members:
            user_item = create_user_item(feide_member, anonymize=anonymize)
            feide_id = user_item.get('feide_id')
            unique_users.add(feide_id)

            affiliations = user_item.get('affiliations', [])
            if 'student' in affiliations:
                memberships[group_id]['students'].append(user_item)
                total_student_memberships += 1
            elif 'faculty' in affiliations:
                memberships[group_id]['teachers'].append(user_item)
                total_teacher_memberships += 1
            else:
                memberships[group_id]['other'].append(user_item)
            total_memberships += 1

        # Periodic progress report every 10 groups
        if (index + 1) % 10 == 0:
            yield {
                "result": {
                    "entity": "membership",
                    "action": "fetch",
                    "errors": errors,
                    "counts": {
                        "teacher_membership":  {"fetched": total_teacher_memberships},
                        "student_membership":  {"fetched": total_student_memberships},
                        "unique_users":         {"fetched": len(unique_users)},
                        "total_membership":    {"fetched": total_memberships},
                    },
                },
                "is_done": False,
            }

    # Write per-school users file
    os.makedirs(school_dir, exist_ok=True)
    memberships_file = os.path.join(school_dir, 'memberships.json')
    with open(memberships_file, "w", encoding="utf-8") as file:
        json.dump(memberships, file, indent=2, ensure_ascii=False)

    yield {
        "result": {
            "entity": "membership",
            "action": "fetch",
            "errors": errors,
            "counts": {
                "teacher_membership":  {"fetched": total_teacher_memberships},
                "student_membership":  {"fetched": total_student_memberships},
                "unique_users":         {"fetched": len(unique_users)},
                "total_memberships":    {"fetched": total_memberships},
            },
        },
        "is_done": True,
    }
