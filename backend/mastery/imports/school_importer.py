import os
import json
from django.utils import timezone
from mastery import models
from .helpers import print_import_statistics

# Get data directory path
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, 'data')

def import_schools_from_file(org_number=None, is_overwrite_enabled=False, is_dryrun_enabled=False):
    """Import schools from file"""
    print(f"👉 import_schools_from_file: BEGIN (org_number={org_number})")
    
    if org_number:
        # Check if school-specific file exists
        school_groups_file = os.path.join(data_dir, 'schools', org_number, 'groups.json')
        if not os.path.exists(school_groups_file):
            raise Exception(f"School {org_number} not found in Feide data. Check org number or fetch groups first.")
        with open(school_groups_file, 'r') as file:
            school_data = json.load(file)
        schools_to_import = school_data.get('schools', [])
    else:
        # Import all schools
        schools_file = os.path.join(data_dir, 'unified', 'schools.json')
        if not os.path.exists(schools_file):
            raise Exception("No schools data found. Run fetch groups first.")
        with open(schools_file, 'r') as file:
            schools_data = json.load(file)
        schools_to_import = []
        for school_info in schools_data.get('schools', []):
            schools_to_import.append({
                'id': school_info['feide_id'],
                'displayName': school_info['display_name'],
                'parent': school_info['parent']
            })
    
    # Import the schools
    stats = import_schools_from_data(
        schools_to_import,
        is_overwrite_enabled=is_overwrite_enabled,
        is_dryrun_enabled=is_dryrun_enabled
    )
    print("✅ import_schools_from_file COMPLETED")
    return stats

def import_schools_from_data(schools_list, is_overwrite_enabled=False, is_dryrun_enabled=False):
    """Helper function to import schools from a list"""
    stats = {'created': 0, 'existing': 0, 'updated': 0, 'failed': 0}
    print(f"🏫 Schools to process: {len(schools_list)}")
    
    for school_data in schools_list:
        feide_id = school_data['id']
        org_number = feide_id.rsplit(':', 1)[-1]
        display_name = school_data['displayName']
        
        existing_school = models.School.objects.filter(feide_id__exact=feide_id).first()
        
        if existing_school:
            if is_overwrite_enabled:
                existing_school.display_name = display_name
                existing_school.maintained_at = timezone.now()
                if len(display_name) == 3:
                    existing_school.short_name = display_name
                if not is_dryrun_enabled:
                    existing_school.save()
                    print(f"  🔄 School updated: {display_name}")
                else:
                    print(f"  🧪 DRY RUN: would update school {display_name}")
                stats['updated'] += 1
            else:
                print(f"  📋 School exists: {existing_school.display_name}")
                stats['existing'] += 1
        else:
            try:
                if not is_dryrun_enabled:
                    new_school = models.School.objects.create(
                        display_name=display_name,
                        org_number=org_number,
                        feide_id=feide_id,
                        maintained_at=timezone.now(),
                    )
                    if len(display_name) == 3:
                        new_school.short_name = display_name
                        new_school.save()
                        print(f"  ✅ School created: {display_name} [short_name: {display_name}]")
                    else:
                        print(f"  ✅ School created: {display_name} [no short_name - displayName not 3 chars]")
                else:
                    print(f"  🧪 DRY RUN: would create school {display_name}")
                stats['created'] += 1
            except Exception as e:
                print(f"  ❌ Failed to create school: {display_name} - Error: {e}")
                stats['failed'] += 1
    
    print_import_statistics('schools', stats)
    return stats
