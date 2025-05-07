import os
import sys
import json
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from mastery import models
import django.db


def import_groups_to_db():
    print("👉 import_groups_to_db: BEGIN")
    groups_file = os.path.join(script_dir, 'data', 'groups.json')
    with open(groups_file) as file:
        groups = json.load(file)

    count = 0
    schools = (groups['fc:org'].get("['primary_and_lower_secondary', 'upper_secondary']", []) +
               groups['fc:org'].get("['upper_secondary', 'primary_and_lower_secondary']", []))

    for school in schools:
        org_number = school["id"].rsplit(':', 1)[-1]
        django.db.close_old_connections()
        existing_school = models.School.objects.filter(org_number__exact=org_number).first()
        if existing_school:
            print("School already exists in DB:", existing_school)
        else:
            new_school = models.School.objects.create(
                display_name=school['displayName'],
                org_number=org_number,
                owner=school['parent'],
                feide_id=school['id'],
            )
            new_school.save()
            count += 1

    # non-school groups (groups minus schools)
    


    print("✅ import_groups_to_db: DONE", count)

if __name__ == "__main__":
    import_groups_to_db()
