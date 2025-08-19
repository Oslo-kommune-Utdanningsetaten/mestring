import os
import sys
import json
import requests
from django.utils import timezone
from requests.structures import CaseInsensitiveDict

# Add the backend directory to Python path and setup Django
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')
backend_dir = os.path.dirname(script_dir)
sys.path.append(backend_dir)

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from mastery import models

TOKEN_ENDPOINT = "https://auth.dataporten.no/oauth/token"
GROUPS_ENDPOINT = "https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups"
FEIDE_CLIENT_ID = os.environ.get('FEIDE_CLIENT_ID')
FEIDE_CLIENT_SECRET = os.environ.get('FEIDE_CLIENT_SECRET')
UDIR_GREP_URL = "https://data.udir.no/kl06/v201906/fagkoder/"


def _run_with_task_tracking(job_name, target_id, func, *args, **kwargs):
    """Simple wrapper to track any import function with DataMaintenanceTask"""
    
    # Create task
    task = models.DataMaintenanceTask.objects.create(
        job_name=job_name,
        target_id=target_id,
        status='pending',
        result={}
    )
    
    try:
        print(f"📋 Starting task: {job_name} (ID: {task.id})")
        
        # Update to running
        task.status = 'running'
        task.started_at = timezone.now()
        task.save()
        
        # Run your existing function
        result = func(*args, **kwargs)
        
        # Mark as finished
        task.status = 'finished'
        task.finished_at = timezone.now()
        task.result = result or {"message": "Completed successfully"}
        task.save()
        
        print(f"✅ Task completed: {job_name} (ID: {task.id})")
        return result
        
    except Exception as e:
        # Mark as failed
        task.status = 'failed'
        task.failed_at = timezone.now()
        task.result = {"error": str(e), "message": f"Task failed: {str(e)}"}
        task.save()
        
        print(f"❌ Task failed: {job_name} (ID: {task.id}) - {e}")
        raise


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

    # Create school-specific group files
    _create_school_specific_group_files(result)

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


def _create_school_specific_group_files(groups_data):
    """Create separate group files for each school in organized directories"""
    print("\n📂 Creating school-specific group files...")
    
    data_dir = os.path.join(script_dir, 'data')
    unified_dir = os.path.join(data_dir, 'unified')
    schools_dir = os.path.join(data_dir, 'schools')
    
    # Create directories
    os.makedirs(unified_dir, exist_ok=True)
    os.makedirs(schools_dir, exist_ok=True)
    
    # Create unified schools.json with basic school info
    schools_info = []
    for school in groups_data['schools']:
        org_number = school["id"].rsplit(':', 1)[-1]
        schools_info.append({
            'org_number': org_number,
            'display_name': school['displayName'],
            'feide_id': school['id'],
            'parent': school['parent']
        })
    
    # Save to unified directory
    schools_file = os.path.join(unified_dir, 'schools.json')
    with open(schools_file, 'w') as file:
        json.dump({
            'fetched_at': timezone.now().isoformat(),
            'schools': schools_info
        }, file, indent=2, ensure_ascii=False)
    print(f"  ✅ Created {schools_file}")
    
    # Create school-specific directories and files
    for school in groups_data['schools']:
        org_number = school["id"].rsplit(':', 1)[-1]
        school_feide_id = school['id']
        
        # Create school directory
        school_dir = os.path.join(schools_dir, org_number)
        os.makedirs(school_dir, exist_ok=True)
        
        # Filter groups belonging to this school
        school_teaching = [g for g in groups_data['teaching'] if g.get('parent') == school_feide_id]
        school_basis = [g for g in groups_data['basis'] if g.get('parent') == school_feide_id]
        
        # Get subjects for this school's teaching groups
        school_subjects = []
        seen_subjects = set()
        for group in school_teaching:
            if 'grep' in group and group['grep'] and 'code' in group['grep']:
                subject_code = group['grep']['code']
                subject_name = group['grep']['displayName']
                subject_key = (subject_code, subject_name)
                if subject_key not in seen_subjects and subject_code:
                    seen_subjects.add(subject_key)
                    school_subjects.append({
                        'code': subject_code,
                        'displayName': subject_name
                    })
        
        school_groups_data = {
            'school_org_number': org_number,
            'school_name': school['displayName'],
            'school_feide_id': school_feide_id,
            'fetched_at': timezone.now().isoformat(),
            'owners': groups_data['owners'],  # Keep owners for all schools
            'schools': [school],  # Just this school
            'teaching': school_teaching,
            'basis': school_basis,
            'subjects': school_subjects,
            'programs': groups_data['programs'],
            'levels': groups_data['levels'],
            'other': [g for g in groups_data['other'] if g.get('parent') == school_feide_id]
        }
        
        # Save school groups file in school directory
        school_groups_file = os.path.join(school_dir, 'groups.json')
        with open(school_groups_file, 'w') as file:
            json.dump(school_groups_data, file, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Created {school_groups_file} ({len(school_teaching)} teaching, {len(school_basis)} basis, {len(school_subjects)} subjects)")
    
    print(f"📂 School-specific directories created in {schools_dir}/")
    print(f"📋 Use 'schools/<org_number>/groups.json' files for school-specific imports")


def ensure_subject(grep_code):
    """Ensure a subject exists in the database, fetching from UDIR if necessary."""
    subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if not subject:
        udir_response = requests.get(UDIR_GREP_URL + grep_code)
        if udir_response.status_code == 200 and udir_response.text:
            udir_subject = udir_response.json()
            print("  Creating subject:", grep_code, udir_subject['tittel'][0]['verdi'])
            display_name = udir_subject['tittel'][0]['verdi']
            short_name = udir_subject['kortform'][0]['verdi']
            grep_group_code = udir_subject['opplaeringsfag'][0]['kode'] if udir_subject.get('opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0 else None
            subject = models.Subject.objects.create(
                display_name=display_name,
                short_name=short_name,
                grep_code=grep_code,
                grep_group_code=grep_group_code,
                maintained_at=timezone.now(),
            )
        else:
            print("🚷Failed to fetch subject from UDIR:", grep_code)
            subject = None
    return subject


def import_schools_to_db():
    """Import schools from the fetched groups JSON file to the database."""
    print("👉 import_schools_to_db: BEGIN")
    
    # Load from the current script directory (where groups.json is stored after fetch)
    groups_file = os.path.join(data_dir, 'unified', 'groups.json')
    
    # Check if groups.json exists
    if not os.path.exists(groups_file):
        print(f"❌ Error: groups.json not found at {groups_file}")
        print("   Please run 'python imports.py fetch' first to fetch groups data")
        return None
        
    with open(groups_file) as file:
        groups = json.load(file)


    django.db.close_old_connections()
    
    # Initialize school-specific statistics
    stats = {
        'schools_created': 0,
        'schools_existing': 0,
        'schools_updated': 0,
        'schools_failed': 0
    }

    # Import schools only
    schools = groups.get('schools', [])
    print(f"🏫 Schools to process: {len(schools)}")
    
    for school in schools:
        try:
    
            org_number = school["id"].rsplit(':', 1)[-1]
            # Check if school already exists
            existing_school = models.School.objects.filter(org_number__exact=org_number).first()
            if existing_school:
                existing_school.maintained_at = timezone.now()
               
                stats['schools_existing'] += 1
            else:
                # Create new school
                new_school = models.School.objects.create(
                    display_name=school['displayName'],
                    org_number=org_number,
                    owner=school['parent'],
                    feide_id=school['id'],
                    maintained_at=timezone.now(), 
                )
                print(f"  ✅ School created: {new_school.display_name}")
                stats['schools_created'] += 1
                
        except Exception as e:
            print(f"  ❌ Failed to process school {school.get('displayName', 'Unknown')}: {e}")
            stats['schools_failed'] += 1

    _print_import_statistics('schools', stats)
    
    return stats


def _ensure_group_exists(group_data, group_type, subject=None):
    """
    Reusable pattern for create-or-update any group type
    Returns (group, created, error_message)
    """
    feide_id = group_data["id"]
    
    # Check if group already exists 
    existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
    if existing_group:
        return existing_group, False, None

    # Find parent school 
    school = models.School.objects.filter(feide_id__exact=group_data['parent']).first()
    if not school:
        return None, False, f"School not found for group {feide_id}"
    
    try: 
        # Create new group
        new_group = models.Group.objects.create(
            display_name=group_data['displayName'],
            type=group_type,
            school=school,
            subject=subject,  
            feide_id=feide_id,
            valid_from=group_data['notBefore'],
            valid_to=group_data['notAfter'],
            maintained_at=timezone.now(),
        )

        return new_group, True, None
    except Exception as e:
        error_message = f"Failed to create group {feide_id}: {str(e)}"
        return None, False, error_message

def _process_subject_for_group(group_data, stats): 
    """
    Handle subject processing for teaching groups
    Returns subject object or None
    """

    if 'grep' not in group_data or 'code' not in group_data['grep']:
        stats['groups_without_subjects'] += 1
        print(f"  ⚠️ No subject code for: {group_data['displayName']}")
        return None
    
    grep_code = group_data['grep']['code']

    # Check if subject exists
    existing_subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if existing_subject:
        stats['subjects_existing'] += 1
        print(f"  📖 Subject exists: {existing_subject.display_name}")
        stats['groups_with_subjects'] += 1  
        return existing_subject
    else:
        # Create new subject and fetch from UDIR
        subject = ensure_subject(grep_code)
        if subject:
            stats['subjects_created'] += 1
            print(f"  ✨ Subject created: {subject.display_name}")
            stats['groups_with_subjects'] += 1
            return subject
        else:
            stats['groups_without_subjects'] += 1
            return None

    
def _import_basis_groups(basis_groups, stats):
    """Import basis groupd from groups data"""
    print(f"\n👥 Basis groups: {len(basis_groups)}")

    for group in basis_groups:
        group_obj, created, error = _ensure_group_exists(group, 'basis')
        if error:
            print(f"  ❌ {error}")
            continue
        if created:
            print(f"  ✅ Basis group created: {group_obj.display_name}")
            stats['basis_groups_created'] += 1
        else:
            print(f"  📋 Basis group already exists: {group_obj.display_name}")
            stats['basis_groups_existing'] += 1

def _import_teaching_groups(teaching_groups, stats):
    """Import teaching groups from groups data"""
    print(f"\n📚 Teaching groups: {len(teaching_groups)}")

    for group in teaching_groups:
        subject = _process_subject_for_group(group, stats) 
        group_obj, created, error = _ensure_group_exists(group, 'teaching', subject)
        
        if error:
            print(f"  ❌ {error}")
            continue
        
        if created:
            print(f"  ✅ Teaching group created: {group_obj.display_name}")
            stats['teaching_groups_created'] += 1
        else:
            print(f"  📋 Teaching group already exists: {group_obj.display_name}")
            stats['teaching_groups_existing'] += 1


def _print_import_statistics(entity_type, stats):
    """Generic statistics printer - handles schools, groups, users"""
    emoji_map = {'schools': '🏫', 'groups': '📊', 'users': '👥'}
    emoji = emoji_map.get(entity_type, '📋')
    
    print(f"\n{emoji} {entity_type.upper()} IMPORT STATISTICS")
    print("="*50)
    
    for key, value in stats.items():
        if 'created' in key:
            print(f"✅ {key.replace('_', ' ').title()}: {value}")
        elif 'existing' in key:
            print(f"📋 {key.replace('_', ' ').title()}: {value}")
        elif 'failed' in key:
            print(f"❌ {key.replace('_', ' ').title()}: {value}")
        else:
            print(f"💡 {key.replace('_', ' ').title()}: {value}")
    
    print("="*50)


def import_groups_to_db(org_number=None):
    """
    Import basis and teaching groups from groups.json or school-specific files to database
    """
    print("👉 import_groups_to_db: BEGIN")
    
    # Load data based on org_number parameter
    if org_number:
        # Load school-specific file
        school_dir = os.path.join(data_dir, 'schools', org_number)
        groups_file = os.path.join(school_dir, 'groups.json')
        
        if not os.path.exists(groups_file):
            print(f"❌ Error: School groups file not found at {groups_file}")
            return None
        
        with open(groups_file, 'r') as file:
            groups_data = json.load(file)
        
        print(f"🏫 Processing groups for school: {groups_data.get('school_name', org_number)}")
        
        # Extract groups from school-specific structure
        groups = {
            'basis': groups_data.get('basis', []),
            'teaching': groups_data.get('teaching', [])
        }
    else:
        # Load unified file
        groups_file = os.path.join(data_dir, 'unified', 'groups.json')
        
        if not os.path.exists(groups_file):
            print(f"❌ Error: groups.json not found at {groups_file}") 
            print("   Please run 'python mastery/imports.py fetch' first")
            return None
        
        with open(groups_file) as file:
            groups = json.load(file)

        for group_type in groups:
            print(f"{group_type}: {len(groups[group_type])}")
        print("--------------------------------\n")

    # Initialize statistics
    django.db.close_old_connections()
    stats = {
        'basis_groups_created': 0,
        'basis_groups_existing': 0,
        'teaching_groups_created': 0,
        'teaching_groups_existing': 0,
        'subjects_created': 0,
        'subjects_existing': 0,       
        'groups_without_subjects': 0,
        'groups_with_subjects': 0
    }

    # Import groups using existing functions
    _import_basis_groups(groups.get('basis', []), stats)
    _import_teaching_groups(groups.get('teaching', []), stats)
    _print_import_statistics('groups', stats)
    
    print("✅ import_groups_to_db COMPLETED")
    return stats


def fetch_feide_users():
    """Fetch users from Feide API for all known groups and create school-specific files"""
    print("BEGIN: fetch_feide_users")
    
    # Check if credentials are set
    if not FEIDE_CLIENT_ID or not FEIDE_CLIENT_SECRET:
        print("Error: FEIDE_CLIENT_ID or FEIDE_CLIENT_SECRET environment variables not set")
        return None

    # Get token
    token_response = requests.post(TOKEN_ENDPOINT, auth=(FEIDE_CLIENT_ID, FEIDE_CLIENT_SECRET), data={'grant_type': 'client_credentials'})
    if token_response.status_code != 200 or not token_response.text:
        print(f"🚷Failed to get token. Status code: {token_response.status_code}")
        return None

    token = token_response.json()['access_token']
    
    # Get all groups from database (that we've already imported)
    django.db.close_old_connections()
    known_groups = models.Group.objects.all()
    result = {}
    
    groups_processed = 0
    groups_failed = 0
    total_users = 0

    for known_group in known_groups:
        print(f"Fetching members of group: {known_group.display_name}")
        
        # Use Groups API members endpoint
        members_url = f"https://groups-api.dataporten.no/groups/orgs/feide.osloskolen.no/groups/{known_group.feide_id.replace('%', '%25')}/members"
        members_response = requests.get(members_url, headers={"Authorization": "Bearer " + token})
        
        if members_response.status_code != 200:
            print(f"  🚷Failed ({members_response.status_code}) to fetch members of: {known_group.feide_id}")
            groups_failed += 1
            continue
            
        if known_group.feide_id not in result:
            result[known_group.feide_id] = {
                "teachers": [],
                "students": [],
                "other": []
            }
            
        feide_group_members = members_response.json()
        group_user_count = 0
        
        for feide_member in feide_group_members:
            member_item = _create_user_item(feide_member)
            if member_item['affiliation'] == 'student':
                result[known_group.feide_id]['students'].append(member_item)
            elif member_item['affiliation'] == 'faculty':
                result[known_group.feide_id]['teachers'].append(member_item)
            else:
                result[known_group.feide_id]['other'].append(member_item)
            group_user_count += 1
            
        print(f"  ✅ Found {group_user_count} users")
        total_users += group_user_count
        groups_processed += 1

    unified_dir = os.path.join(data_dir, 'unified')
    os.makedirs(unified_dir, exist_ok=True)
    
    output_file = os.path.join(unified_dir, 'users.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    # Create school-specific user files
    _create_school_specific_user_files(result)
    
    print(f"📊 Processed {groups_processed} groups successfully")
    print(f"🚷 Failed to process {groups_failed} groups")
    print(f"👥 Total users found: {total_users}")
    print("END: fetch_feide_users")
    
    return {
        "message": "Users fetched and stored successfully",
        "groups_processed": groups_processed,
        "groups_failed": groups_failed,
        "total_users": total_users
    }

def _create_school_specific_user_files(users_data):
    """Create separate user files for each school in organized directories"""
    print("\n📂 Creating school-specific user files...")
    
    data_dir = os.path.join(script_dir, 'data')
    unified_dir = os.path.join(data_dir, 'unified')
    schools_dir = os.path.join(data_dir, 'schools')
    
    # Get schools from unified schools.json
    schools_file = os.path.join(unified_dir, 'schools.json')
    if os.path.exists(schools_file):
        with open(schools_file, 'r') as file:
            schools_info = json.load(file)['schools']
    else:
        # Fallback to database if schools.json doesn't exist
        schools_info = []
        for school in models.School.objects.all():
            schools_info.append({
                'org_number': school.org_number,
                'display_name': school.display_name,
                'feide_id': school.feide_id
            })
    
    # Create users file for each school in their directory
    for school_info in schools_info:
        org_number = school_info['org_number']
        school_feide_id = school_info['feide_id']
        
        # Create school directory if it doesn't exist
        school_dir = os.path.join(schools_dir, org_number)
        os.makedirs(school_dir, exist_ok=True)
        
        # Filter user groups belonging to this school
        school_users_data = {}
        school_user_count = 0
        
        for group_feide_id, group_users in users_data.items():
            # Check if this group belongs to this school
            group = models.Group.objects.filter(feide_id=group_feide_id).first()
            if group and group.school and group.school.feide_id == school_feide_id:
                school_users_data[group_feide_id] = group_users
                school_user_count += len(group_users.get('teachers', [])) + len(group_users.get('students', [])) + len(group_users.get('other', []))
        
        if school_users_data:  # Only create file if school has users
            school_users_file_data = {
                'school_org_number': org_number,
                'school_name': school_info['display_name'],
                'school_feide_id': school_feide_id,
                'fetched_at': timezone.now().isoformat(),
                'groups': school_users_data
            }
            
            # Save school-specific users file in school directory
            school_users_file = os.path.join(school_dir, 'users.json')
            with open(school_users_file, 'w') as file:
                json.dump(school_users_file_data, file, indent=2, ensure_ascii=False)
            
            print(f"  ✅ Created {school_users_file} ({len(school_users_data)} groups, {school_user_count} users)")
    
    print(f"📂 School-specific user files created in {schools_dir}/")
    print(f"📋 Use 'schools/<org_number>/users.json' files for school-specific imports")


def _create_user_item(member):
    """Helper function to create user item from Feide member data - from your existing script"""
    feide_id = member['userid_sec'][0].split(':')[1]
    email = feide_id.replace('@feide.', '@')
    return {
        "feide_id": feide_id,
        "name": member['name'],
        "email": email,
        "affiliation": member['membership'].get('affiliation', None)
    }


def import_users_to_db(org_number=None):
    """Import users from users.json or school-specific users files to database"""
    print("👉 import_users_to_db: BEGIN")
    
    memberships = {}
    
    # Try school-specific file first, then fall back to unified file
    if org_number:
        school_dir = os.path.join(data_dir, 'schools', org_number)
        users_file = os.path.join(school_dir, 'users.json')
        if not os.path.exists(users_file):
            print(f"❌ Error: School-specific users file not found at {users_file}")
            return None
        with open(users_file) as file:
            data = json.load(file)
            # School-specific files have metadata + groups structure
            if isinstance(data, dict) and 'groups' in data:
                memberships = data['groups']
            else:
                memberships = data
    else:
        # Try to find any school-specific files first
        schools_dir = os.path.join(data_dir, 'schools')
        if os.path.exists(schools_dir):
            school_dirs = [d for d in os.listdir(schools_dir) if os.path.isdir(os.path.join(schools_dir, d))]
            
            if school_dirs:
                print(f"📂 Found {len(school_dirs)} school directories, importing all...")
                for school_dir in school_dirs:
                    users_file = os.path.join(schools_dir, school_dir, 'users.json')
                    if os.path.exists(users_file):
                        with open(users_file) as f:
                            data = json.load(f)
                            school_memberships = data.get('groups', {})
                            memberships.update(school_memberships)
        else:
            # Fall back to unified file
            users_file = os.path.join(data_dir, 'unified', 'users.json')
            if not os.path.exists(users_file):
                print(f"❌ Error: No user files found")
                print("   Please run 'python imports.py fetch-users' first")
                return None
            with open(users_file) as file:
                memberships = json.load(file)

    django.db.close_old_connections()
    
    # Ensure roles exist
    teacher_role, student_role = _ensure_roles_exist()
    
    # Initialize statistics
    stats = {
        'users_created': 0,
        'users_existing': 0,
        'memberships_created': 0,
        'memberships_existing': 0,
        'groups_processed': 0,
        'groups_not_found': 0
    }
    
    for group_feide_id in memberships:
        feide_group_memberships = memberships[group_feide_id]
        print(f"\n📋 Processing group: {group_feide_id}")
        print("------------------------------------------------")
        
        group = models.Group.objects.filter(feide_id__exact=group_feide_id).first()
        if not group:
            print("  🚷Group not found in database")
            stats['groups_not_found'] += 1
            continue
            
        stats['groups_processed'] += 1
        
        # Import teachers
        teachers = feide_group_memberships.get('teachers', [])
        print(f"Teachers: {len(teachers)}")
        for teacher in teachers:
            user, created = _ensure_user_exists(teacher)
            if created:
                stats['users_created'] += 1
            else:
                stats['users_existing'] += 1
                
            if user and _ensure_membership(user, group, teacher_role):
                stats['memberships_created'] += 1
            else:
                stats['memberships_existing'] += 1

        # Import students
        students = feide_group_memberships.get('students', [])
        print(f"Students: {len(students)}")
        for student in students:
            user, created = _ensure_user_exists(student)
            if created:
                stats['users_created'] += 1
            else:
                stats['users_existing'] += 1
                
            if user and _ensure_membership(user, group, student_role):
                stats['memberships_created'] += 1
            else:
                stats['memberships_existing'] += 1

    _print_import_statistics('users', stats)
    
    return {
        "message": "Users imported successfully",
        "statistics": stats
    }


def _ensure_roles_exist():
    """Ensure that the roles 'teacher' and 'student' exist - from your existing script"""
    teacher_role, _ = models.Role.objects.get_or_create(
        name='teacher',
        defaults={'maintained_at': timezone.now()}
    )
    student_role, _ = models.Role.objects.get_or_create(
        name='student',
        defaults={'maintained_at': timezone.now()}
    )
    return teacher_role, student_role


def _ensure_user_exists(user_data):
    """Ensure user exists in database, create if not - from your existing script"""
    user = models.User.objects.filter(feide_id__exact=user_data['feide_id']).first()
    if user:
        print(f"  📋 User already exists: {user.email}")
        return user, False
    else:
        user = models.User.objects.create(
            name=user_data['name'],
            feide_id=user_data['feide_id'],
            email=user_data['email'],
            maintained_at=timezone.now(),
        )
        print(f"  ✅ User created: {user.email}")
        return user, True


def _ensure_membership(user, group, role):
    """Ensure user is member of group with role - from your existing script"""
    user_group, created = models.UserGroup.objects.get_or_create(
        user=user,
        group=group,
        role=role,
        defaults={'maintained_at': timezone.now()}
    )
    if created:
        print(f"    ✅ Membership created: {user.email} -> {group.display_name}")
        return True
    else:
        print(f"    📋 Membership exists: {user.email} -> {group.display_name}")
        return False


# School-specific import functions
def import_schools_from_file(org_number=None):
    """Import schools from school-specific group files or all schools from schools.json"""
    print(f"👉 import_schools_from_file: BEGIN (org_number={org_number})")
    
    data_dir = os.path.join(script_dir, 'data')
    
    if org_number:
        # Import single school from groups_<org_number>.json
        school_dir = os.path.join(data_dir, 'schools', org_number)
        school_groups_file = os.path.join(school_dir, 'groups.json')
        if not os.path.exists(school_groups_file):
            print(f"❌ File not found: {school_groups_file}")
            return False
        
        with open(school_groups_file, 'r') as file:
            school_data = json.load(file)
        
        # Extract school info and import
        schools_to_import = school_data.get('schools', [])
        _import_schools_from_list(schools_to_import)
    else:
        # Import all schools from schools.json
        schools_file = os.path.join(data_dir, 'unified', 'schools.json')
        if not os.path.exists(schools_file):
            print(f"❌ File not found: {schools_file}")
            return False
        
        with open(schools_file, 'r') as file:
            schools_data = json.load(file)
        
        # Convert schools info to format expected by import function
        schools_to_import = []
        for school_info in schools_data.get('schools', []):
            schools_to_import.append({
                'id': school_info['feide_id'],
                'displayName': school_info['display_name'],
                'parent': school_info['parent']
            })
        
        _import_schools_from_list(schools_to_import)
    
    print("✅ import_schools_from_file COMPLETED")
    return True


def _import_schools_from_list(schools_list):
    """Helper function to import schools from a list"""
    stats = {'created': 0, 'existing': 0, 'failed': 0}
    
    print(f"🏫 Schools to process: {len(schools_list)}")
    
    for school_data in schools_list:
        feide_id = school_data['id']
        org_number = feide_id.rsplit(':', 1)[-1]
        display_name = school_data['displayName']
        
        existing_school = models.School.objects.filter(feide_id__exact=feide_id).first()
        
        if existing_school:
            print(f"  📋 School exists: {existing_school.display_name}")
            # Update short_name if displayName is 3 characters
            if len(display_name) == 3 and existing_school.short_name != display_name:
                existing_school.short_name = display_name
                existing_school.save()
                print(f"    ✨ Updated short_name: {display_name}")
            stats['existing'] += 1
        else:
            try:
                new_school = models.School.objects.create(
                    display_name=display_name,
                    org_number=org_number,
                    feide_id=feide_id,
                    maintained_at=timezone.now(),
                )
                
                # Set short_name if displayName is exactly 3 characters
                if len(display_name) == 3:
                    new_school.short_name = display_name
                    new_school.save()
                    print(f"  ✅ School created: {display_name} [short_name: {display_name}]")
                else:
                    print(f"  ✅ School created: {display_name} [no short_name - displayName not 3 chars]")
                
                stats['created'] += 1
            except Exception as e:
                print(f"  ❌ Failed to create school: {display_name} - Error: {e}")
                stats['failed'] += 1
    
    _print_import_statistics('schools', stats)
    
if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        org_number = sys.argv[2] if len(sys.argv) > 2 else None
        
        if command == "fetch":
            _run_with_task_tracking('fetch_groups', None, fetch_and_store_feide_groups)
            
        elif command == "fetch-users":
            _run_with_task_tracking('fetch_users', None, fetch_feide_users)
            
        elif command == "import-schools":
            if org_number:
                _run_with_task_tracking('import_schools', org_number, import_schools_from_file, org_number)
            else:
                _run_with_task_tracking('import_schools', None, import_schools_to_db)
                
        elif command == "import-groups":
            if org_number:
                _run_with_task_tracking('import_groups', org_number, import_groups_to_db, org_number)
            else:
                _run_with_task_tracking('import_groups', None, import_groups_to_db)
                
        elif command == "import-users":
            _run_with_task_tracking('import_users', org_number, import_users_to_db, org_number)
            
        elif command == "import-school":
            if not org_number:
                print("❌ Usage: python imports.py import-school <org_number>")
            else:
                print(f"🚀 Complete import for school {org_number}...")
                
                # Simple sequential calls - no need for wrapper function
                _run_with_task_tracking('import_schools', org_number, import_schools_from_file, org_number)
                print()
                _run_with_task_tracking('import_groups', org_number, import_groups_to_db, org_number)
                print()
                _run_with_task_tracking('import_users', org_number, import_users_to_db, org_number)
                
        elif command == "import-all":
            def complete_import():
                print("🚀 Complete system import...")
                
                # Track each operation separately
                _run_with_task_tracking('import_schools', None, import_schools_to_db)
                print()
                _run_with_task_tracking('import_groups', None, import_groups_to_db)
                print()
                _run_with_task_tracking('fetch_users', None, fetch_feide_users)
                print()
                _run_with_task_tracking('import_users', None, import_users_to_db, None)
                
                return {"message": "Complete system import finished"}
            
            _run_with_task_tracking('import_all_complete', None, complete_import)
            
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python mastery/imports.py' to see available commands")
    else:
        print("📋 Available commands:")
        print("  fetch                    - Fetch groups from Feide")
        print("  fetch-users              - Fetch users from Feide")
        print("  import-schools [org]     - Import schools (all or specific)")
        print("  import-groups [org]      - Import groups (all or specific)")
        print("  import-users [org]       - Import users (all or specific)")
        print("  import-school <org>      - Complete import for one school")
        print("  import-all               - Import everything")
        print()
        print("Examples:")
        print("  python mastery/imports.py fetch")
        print("  python mastery/imports.py import-groups NO975291146")
        print("  python mastery/imports.py import-school NO975291146")