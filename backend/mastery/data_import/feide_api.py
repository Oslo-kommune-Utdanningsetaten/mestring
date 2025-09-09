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
    print(f"BEGIN: fetch_feide_groups_for_school_and_store({org_number})")

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
    failure_count = 0
    errors = []
    while next_url:
        try:
            result, next_url = _fetch_groups(next_url, token)
        except Exception as error:
            failure_count += 1
            errors.append(error)

        all_results['basis'].extend(result['basis'])
        all_results['teaching'].extend(result['teaching'])
        all_results['subjects'].extend(result['subjects'])
        success_count = len(all_results['subjects']
                            ) + len(all_results['teaching']) + len(all_results['basis'])
        if index % chunk_size == 0:
            yield {
                "result": {
                    "key": "group-fetch",
                    "entity": "group",
                    "action": "fetch",
                    "total_count": None,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "errors": errors,
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
    output_file = os.path.join(school_dir, 'groups.json')
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"✅ Created school groups file: {output_file}")
    for group_type in all_results:
        print(f"{group_type}: {len(all_results[group_type])}")

    print(f"END: fetch_feide_groups_for_school_and_store({org_number})")
    success_count = len(all_results['subjects']
                        ) + len(all_results['teaching']) + len(all_results['basis'])
    yield {
        "result": {
            "key": "group-fetch",
            "entity": "group",
            "action": "fetch",
            "total_count": None,
            "success_count": success_count,
            "failure_count": failure_count,
            "errors": errors,
        },
        "is_done": True,
    }


def fetch_feide_users_for_school_and_store(
        org_number: str, is_overwrite_enabled=False, is_crash_on_error_enabled=False):
    """Fetch users/memberships for one school by reading its groups.json and hitting Feide members API."""
    print(f"BEGIN: fetch_feide_users_for_school_and_store({org_number})")

    token = get_feide_access_token()

    # Ensure per-school groups file exists
    school_dir = os.path.join(data_dir, org_number)
    groups_file = os.path.join(school_dir, 'groups.json')
    if not os.path.exists(groups_file):
        raise Exception(f"Groups file not found for school {org_number}. Fetch groups first.")

    # Load per-school groups
    with open(groups_file, 'r') as f:
        groups_data = json.load(f)

    # Collect group ids (basis + teaching are what we care about for memberships)
    basis_groups = groups_data.get('basis', []) or []
    teaching_groups = groups_data.get('teaching', []) or []
    all_groups = basis_groups + teaching_groups

    result = {}
    groups_processed = 0
    total_memberships = 0
    unique_users = set()

    # Progress tracking
    total_groups = len(all_groups)
    print(f"📊 Processing {total_groups} groups for school {org_number}")

    for index, group in enumerate(all_groups, 1):
        group_id = group.get('id')
        display_name = group.get('displayName', '')
        if not group_id:
            continue

        # Progress logging
        print(f"  📥 Processing group {index}/{total_groups}: {display_name}")

        # Percent-encode the full Feide id when placing in the URL path
        members_url = f"{MEMEBERS_URL}/{quote(group_id, safe='')}/members"

        members_response = requests.get(members_url, headers={"Authorization": "Bearer " + token})
        if members_response.status_code != 200:
            print(f"    ⚠️ Failed to fetch group {group_id} - skipping ({members_response.status_code})")
            continue

        result[group_id] = {"teachers": [], "students": [], "other": []}
        feide_group_members = members_response.json() or []

        for feide_member in feide_group_members:
            user_item = create_user_item(feide_member)
            feide_id = user_item.get('feide_id')

            unique_users.add(feide_id)

            affiliation = (user_item.get('affiliation') or '').lower()
            if affiliation == 'student':
                result[group_id]['students'].append(user_item)
            elif affiliation == 'faculty':
                result[group_id]['teachers'].append(user_item)
            else:
                result[group_id]['other'].append(user_item)
            total_memberships += 1

        groups_processed += 1

    # Write per-school users file
    os.makedirs(school_dir, exist_ok=True)
    users_file = os.path.join(school_dir, 'users.json')
    with open(users_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Created school users file: {users_file}")
    print(
        f"✅ Processed {groups_processed} groups, {len(unique_users)} unique users, {total_memberships} total memberships")
    print(f"END: fetch_feide_users_for_school_and_store({org_number})")

    return {
        "message": "Users fetched successfully",
        "org_number": org_number,
        "groups_processed": groups_processed,
        "unique_users": len(unique_users),
        "total_memberships": total_memberships,
        "total_groups": total_groups,
        "progress": f"{groups_processed}/{total_groups}",
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
