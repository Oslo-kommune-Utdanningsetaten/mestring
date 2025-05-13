import os
import sys
import json
from django.core import serializers
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from mastery import models


def output_something():
    print("👉 output_something: BEGIN")
    result = {
        "groups": []
    }
    groups = models.Group.objects.all()
    for group in groups:
        students = group.get_students()
        teachers = group.get_teachers()
        if len(students) == 0 or len(teachers) == 0:
            print(f"🚷Group {group.feide_id} has no students or teachers")
            continue
        students_json_str = serializers.serialize('json', students)
        teachers_json_str = serializers.serialize('json', teachers)
        group_data = {
            "id": group.id,
            "feide_id": group.feide_id,
            "display_name": group.display_name,
            "students": json.loads(students_json_str),
            "teachers": json.loads(teachers_json_str)
        }
        # add group data to result
        result["groups"].append(group_data)
    # Write the result to a JSON file

    output_file = os.path.join(script_dir, 'data', 'temp_dump.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("✅ output_something")

if __name__ == "__main__":
    output_something()
