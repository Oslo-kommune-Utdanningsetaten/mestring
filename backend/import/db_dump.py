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
    students = models.User.objects.filter(user_groups__role__name='student')
    students_json_str = serializers.serialize('json', students)
    result = {
        "students": json.loads(students_json_str),
    }

    output_file = os.path.join(script_dir, 'data', 'temp_dump.json')
    with open(output_file, "w") as file:
        json.dump(result, file, indent=2, ensure_ascii=False)

    print("✅ output_something")

if __name__ == "__main__":
    output_something()
