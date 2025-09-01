import os
import json
import requests
from django.utils import timezone
from requests.structures import CaseInsensitiveDict
from mastery import models
from .helpers import create_user_item, get_feide_access_token
from urllib.parse import quote

# API Configuration
TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups"
FEIDE_CLIENT_ID = os.environ.get('FEIDE_CLIENT_ID')
FEIDE_CLIENT_SECRET = os.environ.get('FEIDE_CLIENT_SECRET')
UDIR_GREP_URL = "https://data.udir.no/kl06/v201906/fagkoder/"
FEIDE_REALM = "feide.osloskolen.no"
GROUPS_BASE = "https://groups-api.dataporten.no/groups/v1"

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data') 
_subject_cache = {}

def _fetch_groups(url, token, result):
    """Helper function for pagination """
    groups_response = requests.get(url, headers={"Authorization": "Bearer " + token})
    groups = groups_response.json()

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
        elif group_type == 'fc:gogroup' and group_go_type == 'p':
            result['programs'].append(group)
        elif group_type == 'fc:gogroup' and group_go_type == 'l':
            result['levels'].append(group)
        else:
            result['other'].append(group)
            
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


def fetch_and_store_feide_groups_for_school(org_number: str):
    """Fetch groups for a single school (by org number) and store them in a per-school file."""
    print(f"BEGIN: fetch_and_store_feide_groups_for_school({org_number})")

    token = get_feide_access_token()

    result = {
        "owners": [],   # skoleeiere
        "schools": [],  # skoler
        "teaching": [], # undervisningsgrupper
        "basis": [],    # basisgrupper
        "subjects": [], # fag
        "programs": [], # programgrupper
        "levels": [],   # nivågrupper
        "other": [],    # andre grupper vi kan ha interesse av?
    }

    # Page through org-scoped groups using the orgunit filter
    next_url = f"{GROUPS_ENDPOINT}?orgunit={org_number}"
    while next_url:
        result, next_url = _fetch_groups(next_url, token, result)

    # Deduplicate subjects by code
    seen = set()
    unique_subjects = []
    for s in result['subjects']:
        code = s.get('code')
        if code and code not in seen:
            unique_subjects.append(s)
            seen.add(code)
    result['subjects'] = unique_subjects

    # Write to per-school file
    school_dir = os.path.join(data_dir, org_number)
    os.makedirs(school_dir, exist_ok=True)
    output_file = os.path.join(school_dir, 'groups.json')
    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Created school groups file: {output_file}")
    for group_type in result:
        print(f"{group_type}: {len(result[group_type])}")

    print(f"END: fetch_and_store_feide_groups_for_school({org_number})")

    return {
        "message": "School groups fetched successfully",
        "org_number": org_number,
        "teaching_groups": len(result['teaching']),
        "basis_groups": len(result['basis']),
        "subjects": len(result['subjects']),
        "total_groups": len(result['teaching']) + len(result['basis'])
    }


def fetch_feide_users_for_school(org_number: str):
    """Fetch users/memberships for one school by reading its groups.json and hitting Feide members API."""
    print(f"BEGIN: fetch_feide_users_for_school({org_number})")

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

    for i, g in enumerate(all_groups, 1):
        group_id = g.get('id')
        display_name = g.get('displayName', '')
        if not group_id:
            continue

        # Progress logging
        print(f"  📥 Processing group {i}/{total_groups}: {display_name}")

        # Percent-encode the full Feide id when placing in the URL path
        members_url = f"https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups/{quote(group_id, safe='')}/members"

        members_response = requests.get(members_url, headers={"Authorization": "Bearer " + token})
        if members_response.status_code != 200:
            print(f"    ⚠️ Failed to fetch group {group_id} - skipping ({members_response.status_code})")
            continue

        result[group_id] = {"teachers": [], "students": [], "other": []}
        feide_group_members = members_response.json() or []

        for feide_member in feide_group_members:
            member_item = create_user_item(feide_member)
            feide_id = member_item.get('feide_id')

            if feide_id:
                unique_users.add(feide_id)

            affiliation = (member_item.get('affiliation') or '').lower()
            if affiliation == 'student':
                result[group_id]['students'].append(member_item)
            elif affiliation == 'faculty':
                result[group_id]['teachers'].append(member_item)
            else:
                result[group_id]['other'].append(member_item)
            total_memberships += 1

        groups_processed += 1
        
    # Write per-school users file
    os.makedirs(school_dir, exist_ok=True)
    users_file = os.path.join(school_dir, 'users.json')
    with open(users_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ Created school users file: {users_file}")
    print(f"✅ Processed {groups_processed} groups, {len(unique_users)} unique users, {total_memberships} total memberships")
    print(f"END: fetch_feide_users_for_school({org_number})")

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
        raise Exception(f"Failed to fetch groups for org {org_number}: {response.status_code} {response.text}")
    return response.json()


def ensure_subject(grep_code, is_dryrun_enabled=False):
    """Ensure a subject exists in the database, fetching from UDIR if necessary."""
    subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if grep_code in _subject_cache:
        return _subject_cache[grep_code]
    if not subject:
        udir_response = requests.get(UDIR_GREP_URL + grep_code)
        if udir_response.status_code == 200 and udir_response.text:
            udir_subject = udir_response.json()
            display_name = udir_subject['tittel'][0]['verdi']
            short_name = udir_subject['kortform'][0]['verdi']
            grep_group_code = udir_subject['opplaeringsfag'][0]['kode'] if udir_subject.get('opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0 else None
            
            if not is_dryrun_enabled:
                print("  Creating subject:", grep_code, display_name)
                subject = models.Subject.objects.create(
                    display_name=display_name,
                    short_name=short_name,
                    grep_code=grep_code,
                    grep_group_code=grep_group_code,
                    maintained_at=timezone.now(),
                )
            else:
                print(f"  🧪 DRY RUN: would create subject {grep_code} - {display_name}")
                # Return unsaved instance for dry-run
                subject = models.Subject(
                    display_name=display_name,
                    short_name=short_name,
                    grep_code=grep_code,
                    grep_group_code=grep_group_code,
                    maintained_at=timezone.now(),
                )
        else:
            print("🚷Failed to fetch subject from UDIR:", grep_code)
            subject = None
    _subject_cache[grep_code] = subject
    return subject
