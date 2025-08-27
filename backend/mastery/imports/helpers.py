import os
import json
from django.utils import timezone
from mastery import models

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

def print_import_statistics(entity_type, stats):
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

def create_user_item(member):
    """Helper function to create user item from Feide member data"""
    feide_id = member['userid_sec'][0].split(':')[1]
    email = feide_id.replace('@feide.', '@')
    return {
        "feide_id": feide_id,
        "name": member['name'],
        "email": email,
        "affiliation": member['membership'].get('affiliation', None)
    }

def create_school_specific_group_files(groups_data):
    """Create separate group files for each school in organized directories"""
    print("\n📂 Creating school-specific group files...")
    
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
    print("📋 Use 'schools/<org_number>/groups.json' files for school-specific imports")

def create_school_specific_user_files(users_data):
    """Create separate user files for each school in organized directories"""
    print("\n📂 Creating school-specific user files...")
    
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
    print("📋 Use 'schools/<org_number>/users.json' files for school-specific imports")

def check_school_data_status(org_number):
    """Check what data files exist for a school"""
    school_dir = os.path.join(data_dir, 'schools', org_number)
    
    status = {
        'groups_file_exists': os.path.exists(os.path.join(school_dir, 'groups.json')),
        'users_file_exists': os.path.exists(os.path.join(school_dir, 'users.json'))
    }
    
    return status