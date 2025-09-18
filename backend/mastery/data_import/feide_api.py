import os
import json
import requests
from django.utils import timezone
from requests.structures import CaseInsensitiveDict
from mastery import models
from .helpers import create_user_item, get_feide_access_token
from urllib.parse import quote

# API Configuration
GROUPS_ENDPOINT = os.environ.get('GROUPS_ENDPOINT')
FEIDE_REALM = os.environ.get('FEIDE_REALM')
GROUPS_BASE = os.environ.get('GROUPS_BASE')
MEMEBERS_URL = os.environ.get('MEMEBERS_URL')

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')


def _fetch_groups(url, token):
    """Helper function for pagination """
    try:
        groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
        groups = groups_response.json()
    except Exception as error:
        raise Exception(
            {"error": "fetch-error", "message": f"Failed to fetch groups from Feide: {str(error)[:1000]}"})

    result = {
        "owners": [],   # skoleeiere
        "schools": [],  # skoler
        "teaching": [],  # undervisningsgrupper
        "basis": [],    # basisgrupper
        "subjects": [],  # fag
    }
    # Append groups to accumulated result
    for group in groups:
        group_type = group['type']
        group_go_type = group.get('go_type', None)

        # by definition, school owners do not have the parent key
        # https://docs.feide.no/reference/apis/groups_api/group_types/pse_school_owner.html

        if group_type == 'fc:org':
            if 'parent' in group:
                result['schools'].append(group)
            else:
                result['owners'].append(group)
        elif group_type == 'fc:gogroup' and group_go_type == 'u':
            result['teaching'].append(group)
            if 'grep' in group and group['grep']:
                subject_code = group['grep']['code']
                subject_name = group['grep']['displayName']
                if subject_code:
                    result['subjects'].append({
                        'code': subject_code,
                        'displayName': subject_name
                    })
        elif group_type == 'fc:gogroup' and group_go_type == 'b':
            result['basis'].append(group)

    # Check for pagination
    next_url = None
    if 'Link' in groups_response.headers:
        link_header = CaseInsensitiveDict(groups_response.headers)['Link']
        links = requests.utils.parse_header_links(link_header)
        for link in links:
            if 'rel' in link and link['rel'] == 'next':
                next_url = link['url']
                break

    return result, next_url


def fetch_groups_from_feide(org_number: str):
    """Fetch groups for a single school (by org number) and store them in a per-school file."""
    token = get_feide_access_token()

    all_results = {
        "owners": [],   # skoleeiere
        "schools": [],  # skoler
        "teaching": [],  # undervisningsgrupper
        "basis": [],    # basisgrupper
        "subjects": [],  # fag
    }

    # Page through org-scoped groups using the orgunit filter
    next_url = f"{GROUPS_ENDPOINT}?orgunit={org_number}"
    index = 0
    chunk_size = 10
    errors = []

    while next_url:
        try:
            result, next_url = _fetch_groups(next_url, token)
        except Exception as error:
            errors.append({"error": "fetch-error", "message": str(error)[:1000]})

        # Accumulate results
        all_results["basis"].extend(result.get("basis", []))
        all_results["teaching"].extend(result.get("teaching", []))
        all_results["subjects"].extend(result.get("subjects", []))
        all_results["owners"].extend(result.get("owners", []))
        all_results["schools"].extend(result.get("schools", []))

        index += 1
        if index % chunk_size == 0:
            yield {
                "result": {
                    "entity": "group",
                    "action": "fetch",
                    "errors": errors,
                    "counts": {
                        "basis_group":    {"fetched": len(all_results["basis"])},
                        "teaching_group": {"fetched": len(all_results["teaching"])},
                        "subject":        {"fetched": len(all_results["subjects"])},
                    },
                },
                "is_done": False,
            }

    # Deduplicate subjects by code
    seen = set()
    unique_subjects = []
    for subject in all_results['subjects']:
        code = subject.get('code')
        if code and code not in seen:
            unique_subjects.append(subject)
            seen.add(code)
    all_results['subjects'] = unique_subjects

    # Write to per-school file
    school_dir = os.path.join(data_dir, org_number)
    os.makedirs(school_dir, exist_ok=True)
    groups_file = os.path.join(school_dir, 'groups.json')
    with open(groups_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    for group_type in all_results:
        print(f"{group_type}: {len(all_results[group_type])}")

    yield {
        "result": {
            "entity": "group",
            "action": "fetch",
            "errors": errors,
            "counts": {
                "basis_group":    {"fetched": len(all_results["basis"])},
                "teaching_group": {"fetched": len(all_results["teaching"])},
                "subject":        {"fetched": len(all_results["subjects"])},
            },
        },
        "is_done": True,
    }


def fetch_memberships_from_feide(org_number: str):
    """Fetch memberships for one school by reading its groups.json and hitting Feide members API."""
    print(f"👉 fetch_memberships_from_feide({org_number})")
    token = get_feide_access_token()

    # Ensure per-school groups file exists
    school_dir = os.path.join(data_dir, org_number)
    groups_file = os.path.join(school_dir, 'groups.json')
    if not os.path.exists(groups_file):
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
    print(f"📊 Processing memberships for {total_group_count} groups")

    for index, group in enumerate(all_groups):
        group_id = group.get('id')
        if not group_id:
            group_name = group.get('displayName', 'unknown')
            errors.append({"error": "data-error", "message": f"Group without id {group_name}"})
            continue

        print(f"{index}/{total_group_count}")

        # Percent-encode the full Feide id when placing in the URL path
        group_members_url = f"{MEMEBERS_URL}/{quote(group_id, safe='')}/members"
        # Fetch members for this group
        members_response = requests.get(group_members_url, headers={"Authorization": "Bearer " + token})

        if members_response.status_code != 200:
            errors.append({"error": "fetch-error", "message": f"Failed to fetch members for group {group_id}"})
            continue

        memberships[group_id] = {"teachers": [], "students": [], "other": []}
        feide_group_members = members_response.json() or []

        # Track memberships by role

        for feide_member in feide_group_members:
            user_item = create_user_item(feide_member)
            feide_id = user_item.get('feide_id')
            unique_users.add(feide_id)

            affiliation = (user_item.get('affiliation') or '').lower()
            if affiliation == 'student':
                memberships[group_id]['students'].append(user_item)
                total_student_memberships += 1
            elif affiliation == 'faculty':
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
                        "teacher_memberships":  {"fetched": total_teacher_memberships},
                        "student_memberships":  {"fetched": total_student_memberships},
                        "unique_users":         {"fetched": len(unique_users)},
                        "total_memberships":    {"fetched": total_memberships},
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
                "teacher_memberships":  {"fetched": total_teacher_memberships},
                "student_memberships":  {"fetched": total_student_memberships},
                "unique_users":         {"fetched": len(unique_users)},
                "total_memberships":    {"fetched": total_memberships},
            },
        },
        "is_done": True,
    }


def fetch_school_group(org_number, access_token):
    """Fetch groups for one school by org number"""
    school_group_id = f"fc:org:{FEIDE_REALM}:unit:{org_number}"
    endpoint_url = f"{GROUPS_BASE}/orgs/{FEIDE_REALM}/groups/{quote(school_group_id, safe='')}"

    response = requests.get(endpoint_url, headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch groups for org {org_number}: {response.status_code} {response.text}")
    return response.json()
