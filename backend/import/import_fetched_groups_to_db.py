import os
import sys
import json
import requests
from dotenv import load_dotenv
from django.utils import timezone


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from mastery import models
UDIR_GREP_URL = "https://data.udir.no/kl06/v201906/fagkoder/"

        
# Create a new subject if it doesn't exist
def ensure_subject(grep_code):
    if not grep_code:
        return None
    subject = models.Subject.objects.filter(grep_code__exact=grep_code).first()
    if not subject:
        udir_response = requests.get(UDIR_GREP_URL + grep_code)
        if udir_response.status_code == 200 and udir_response.text:
            udir_subject = udir_response.json()
            print("  Creating subject:", grep_code, udir_subject['tittel'][0]['verdi'])
            diplay_name = udir_subject['tittel'][0]['verdi']
            short_name = udir_subject['kortform'][0]['verdi']
            grep_group_code = udir_subject['opplaeringsfag'][0]['kode'] if udir_subject.get('opplaeringsfag') and len(udir_subject['opplaeringsfag']) > 0 else None
            subject = models.Subject.objects.create(
                display_name=diplay_name,
                short_name=short_name,
                grep_code=grep_code,
                grep_group_code=grep_group_code,
                maintained_at=timezone.now(),
            )
        else:
            print("🚷Failed to fetch subject from UDIR:", grep_code)
            subject = None
    return subject


def import_groups_to_db():
    print("👉 import_groups_to_db: BEGIN")
    groups_file = os.path.join(script_dir, 'data', 'groups.json')
    with open(groups_file) as file:
        groups = json.load(file)

    # print all groups within each category
    for group_type in groups:
        print(f"{group_type}: {len(groups[group_type])}")
    print("--------------------------------\n")

    django.db.close_old_connections()

    # Import schools
    schools = groups.get('schools', [])
    print("\nSchools:", len(schools))
    for school in schools:
        org_number = school["id"].rsplit(':', 1)[-1]
        existing_school = models.School.objects.filter(org_number__exact=org_number).first()
        if existing_school:
            print("  School exists:", existing_school.display_name)
        else:
            new_school = models.School.objects.create(
                display_name=school['displayName'],
                org_number=org_number,
                owner=school['parent'],
                feide_id=school['id'],
                maintained_at=timezone.now(),
            )
            new_school.save()
            print("  School created!", new_school.display_name)

    # Import basis groups
    basis_groups = groups.get('basis', [])
    print("\nBasis groups:", len(basis_groups))
    for group in basis_groups:
        feide_id = group["id"]
        existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
        if existing_group:
            print("  Group exists:", existing_group.display_name)
        else:
            school = models.School.objects.filter(feide_id__exact=group['parent']).first()
            if school:
                school_short_name = feide_id.split(':')[5].split('-')[0] # gotcha!
                school.ensure_short_name(school_short_name)
                new_group = models.Group.objects.create(
                    display_name=group['displayName'],
                    type='basis',
                    school=school,
                    feide_id=feide_id,
                    valid_from=group['notBefore'],
                    valid_to=group['notAfter'],
                    maintained_at=timezone.now(),
                )
                new_group.save()
                print("  Basis group created!", new_group.display_name)
            else:
                print("  School not found for basis group:", feide_id)

    # Import teaching groups
    teaching_groups = groups.get('teaching', [])
    print("\nTeaching groups:", len(teaching_groups))
    for group in teaching_groups:
        feide_id = group["id"]
        existing_group = models.Group.objects.filter(feide_id__exact=feide_id).first()
        if existing_group:
            print("  Group exists:", existing_group.display_name)
        else:
            school = models.School.objects.filter(feide_id__exact=group['parent']).first()
            if school:
                grep_data = group.get('grep', {})
                grep_code = grep_data.get('code') if grep_data else None
                if grep_code:
                    subject = ensure_subject(grep_code)
                else:
                    subject = None
                new_group = models.Group.objects.create(
                    display_name=group['displayName'],
                    type='teaching',
                    school=school,
                    subject=subject,
                    feide_id=feide_id,
                    valid_from=group['notBefore'],
                    valid_to=group['notAfter'],
                    maintained_at=timezone.now(),
                )
                new_group.save()
                print("  Teaching group created!", new_group.display_name)
            else:
                print("  School not found for teaching group:", feide_id)

    print("✅ import_groups_to_db")

if __name__ == "__main__":
    import_groups_to_db()
