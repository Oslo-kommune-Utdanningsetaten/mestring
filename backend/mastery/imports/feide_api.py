import os
import json
import requests
from django.utils import timezone
from requests.structures import CaseInsensitiveDict
from mastery import models
from .helpers import create_school_specific_group_files, create_school_specific_user_files, create_user_item

# API Configuration
TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups"
FEIDE_CLIENT_ID = os.environ.get('FEIDE_CLIENT_ID')
FEIDE_CLIENT_SECRET = os.environ.get('FEIDE_CLIENT_SECRET')
UDIR_GREP_URL = "https://data.udir.no/kl06/v201906/fagkoder/"

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data') 

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

def fetch_and_store_feide_groups():
    """Fetch groups from Feide API and save to groups.json + create school-specific files"""
    print("BEGIN: fetch_and_store_feide_groups")
    # Check if credentials are set
    if not FEIDE_CLIENT_ID or not FEIDE_CLIENT_SECRET:
        print("Error: FEIDE_CLIENT_ID or FEIDE_CLIENT_SECRET environment variables not set")
        return

    # Get token
    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_CLIENT_ID, FEIDE_CLIENT_SECRET), data={'grant_type': 'client_credentials'})

    if token_response.status_code == 200 and token_response.text:
        token = token_response.json()['access_token']
    else:
        print(f"Failed to get token. Status code: {token_response.status_code}")
        return

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
    next_url = GROUPS_ENDPOINT
    while next_url:
        # keep fetching until there are no more pages
        result, next_url = _fetch_groups(next_url, token, result)

    # Remove duplicate subjects
    seen = set()
    unique_subjects = []
    for s in result['subjects']:
        code = s.get('code')
        if code and code not in seen:
            unique_subjects.append(s)
            seen.add(code)
    result['subjects'] = unique_subjects

    unified_dir = os.path.join(data_dir, 'unified')
    os.makedirs(unified_dir, exist_ok=True)
    
    output_file = os.path.join(unified_dir, 'groups.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    
    print(f"✅ Created unified groups file: {output_file}")

    # Create school-specific group files
    create_school_specific_group_files(result)

    for group_type in result:
        print(f"{group_type}: {len(result[group_type])}")
    print("END: fetch_and_store_feide_groups")
    
    return {
        "message": "Groups fetched successfully",
        "schools": len(result['schools']),
        "teaching_groups": len(result['teaching']),
        "basis_groups": len(result['basis']),
        "subjects": len(result['subjects']),
        "total_groups": len(result['teaching']) + len(result['basis'])
    }

def fetch_feide_users(org_number=None):
    """Fetch users from Feide API - SIMPLIFIED"""
    print("BEGIN: fetch_feide_users")
    
    # Simple validation
    if not FEIDE_CLIENT_ID or not FEIDE_CLIENT_SECRET:
        raise Exception("FEIDE credentials not configured")

    # Get token
    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_CLIENT_ID, FEIDE_CLIENT_SECRET), data={'grant_type': 'client_credentials'})
    if token_response.status_code != 200:
        raise Exception(f"Failed to get Feide token: {token_response.status_code}")

    token = token_response.json()['access_token']
    
    # Get groups for this school
    if org_number:
        known_groups = models.Group.objects.filter(school__org_number=org_number)
        if not known_groups.exists():
            raise Exception(f"No groups found for school {org_number}. Import groups first.")
    else: 
        known_groups = models.Group.objects.all()

    result = {}
    groups_processed = 0
    total_users = 0

    for known_group in known_groups:
        print(f"Fetching members of group: {known_group.display_name}")
        
        members_url = f"https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups/{known_group.feide_id.replace('%', '%25')}/members"
        members_response = requests.get(members_url, headers={"Authorization": "Bearer " + token})
        
        if members_response.status_code != 200:
            print(f"  ⚠️ Failed to fetch group {known_group.feide_id} - skipping")
            continue
            
        result[known_group.feide_id] = {
            "teachers": [],
            "students": [],
            "other": []
        }
            
        feide_group_members = members_response.json()
        
        for feide_member in feide_group_members:
            member_item = create_user_item(feide_member)
            if member_item['affiliation'] == 'student':
                result[known_group.feide_id]['students'].append(member_item)
            elif member_item['affiliation'] == 'faculty':
                result[known_group.feide_id]['teachers'].append(member_item)
            else:
                result[known_group.feide_id]['other'].append(member_item)
            total_users += 1
            
        groups_processed += 1

    unified_dir = os.path.join(data_dir, 'unified')
    os.makedirs(unified_dir, exist_ok=True)
    
    output_file = os.path.join(unified_dir, 'users.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)
    
    print(f"✅ Created unified users file: {output_file}")

    create_school_specific_user_files(result)
    
    print(f"✅ Processed {groups_processed} groups, {total_users} users")
    print("END: fetch_feide_users")
    
    return {
        "message": "Users fetched successfully",
        "groups_processed": groups_processed,
        "total_users": total_users
    }

def ensure_subject(grep_code, is_dryrun_enabled=False):
    """Ensure a subject exists in the DB, fetching from UDIR if necessary.
       In dry run: fetch metadata but DO NOT write; return an unsaved instance.
    """
    subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if subject:
        return subject

    # Fetch metadata from UDIR (read-only network)
    udir_response = requests.get("https://data.udir.no/kl06/v201906/fagkoder/" + grep_code)
    if udir_response.status_code == 200 and udir_response.text:
        udir_subject = udir_response.json()
        display_name = udir_subject['tittel'][0]['verdi']
        short_name = udir_subject['kortform'][0]['verdi']
        grep_group_code = (
            udir_subject['opplaeringsfag'][0]['kode']
            if udir_subject.get('opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0
            else None
        )

        if is_dryrun_enabled:
            print("  🧪 DRY RUN: would create subject:", grep_code, display_name)
            # Return an UNSAVED instance for logging/flow consistency
            return models.Subject(
                display_name=display_name,
                short_name=short_name,
                grep_code=grep_code,
                grep_group_code=grep_group_code,
                maintained_at=timezone.now(),
            )

        print("  Creating subject:", grep_code, display_name)
        return models.Subject.objects.create(
            display_name=display_name,
            short_name=short_name,
            grep_code=grep_code,
            grep_group_code=grep_group_code,
            maintained_at=timezone.now(),
        )

    print("🚷Failed to fetch subject from UDIR:", grep_code)
    return None