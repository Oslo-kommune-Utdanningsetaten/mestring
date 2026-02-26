import os
import json
import requests
from requests.structures import CaseInsensitiveDict
from .helpers import get_feide_access_token
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

# API Configuration
GROUPS_ENDPOINT = os.environ.get('GROUPS_ENDPOINT')
FEIDE_REALM = os.environ.get('FEIDE_REALM')
GROUPS_BASE = os.environ.get('GROUPS_BASE')

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')


def _fetch_groups(url, token):
    """Helper function for pagination """
    groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
    if groups_response.status_code != 200:
        logger.error("Failed to fetch groups: %d %s", groups_response.status_code, groups_response.text)
        raise Exception(f"Failed to fetch groups: {groups_response.status_code}: {groups_response.text}")

    groups = groups_response.json()

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
        result, next_url = _fetch_groups(next_url, token)

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
        logger.debug("Fetched %d %s groups", len(all_results[group_type]), group_type)

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


def fetch_school_group(org_number, access_token):
    """Fetch groups for one school by org number"""
    school_group_id = f"fc:org:{FEIDE_REALM}:unit:{org_number}"
    endpoint_url = f"{GROUPS_BASE}/orgs/{FEIDE_REALM}/groups/{quote(school_group_id, safe='')}"

    response = requests.get(endpoint_url, headers={"Authorization": f"Bearer {access_token}"})
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch groups for org {org_number}: {response.status_code} {response.text}")
    return response.json()
