import os
import sys
import json
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

def ensure_mastery_schema_exists():
    title = 'Mestringstrappa'
    mastery_schema = models.MasterySchema.objects.filter(title=title).first()
    if not system_user:
        print("Creating default mastery_schema:", title)
        system_user = models.MasterySchema.objects.create(
            title=title,
            description='Mestring angitt med fem nivåer, fra "aldri" til "mestrer".',
            maintained_at=timezone.now(),
            schema={
                "levels": [
                    {
                    "text": "Mestrer ikke",
                    "color": "rgb(229, 50, 43)",
                    "maxValue": 20,
                    "minValue": 1
                    },
                    {
                    "text": "Mestrer sjelden",
                    "color": "rgb(159, 113, 202)",
                    "maxValue": 40,
                    "minValue": 21
                    },
                    {
                    "text": "Mestrer iblant",
                    "color": "rgb(86, 174, 232)",
                    "maxValue": 60,
                    "minValue": 41
                    },
                    {
                    "text": "Mestrer ofte",
                    "color": "rgb(241, 249, 97)",
                    "maxValue": 80,
                    "minValue": 61
                    },
                    {
                    "text": "Mestrer",
                    "color": "rgb(160, 207, 106)",
                    "maxValue": 100,
                    "minValue": 81
                    }
                ],
                "inputIncrement": 1,
                "renderDirection": "vertical",
                "isColorGradientEnabled": False
            }
        )
        mastery_schema.save()
    return mastery_schema


def ensure_roles_exist():
    """
    Ensure that the roles 'teacher' and 'student' exist in the database.
    If they do not exist, create them.
    """
    teacher_role, _ = models.Role.objects.get_or_create(
        name='teacher',
        defaults={'maintained_at': timezone.now()}
    )
    student_role, _ = models.Role.objects.get_or_create(
        name='student',
        defaults={'maintained_at': timezone.now()}
    )
    return teacher_role, student_role

# Create a new subject if it doesn't exist
def ensure_membership(user, group, role):
    """
    Ensure that a user is a member of a group with the specified role.
    If the user is not already a member, create the membership.
    """
    user_group, created = models.UserGroup.objects.get_or_create(
        user=user,
        group=group,
        role=role,
        defaults={'maintained_at': timezone.now()}
    )
    if created:
        print("  Membership created!", user_group.id)
    else:
        print("  Membership already exists!", user_group.id)
    return user_group



def import_users_to_db():
    print("👉 import_users_to_db: BEGIN")
    teacher_role, student_role = ensure_roles_exist()
    memberships_file = os.path.join(script_dir, 'data', 'users.json')
    with open(memberships_file) as file:
        memberships = json.load(file)

    django.db.close_old_connections()
    
    for group_feide_id in memberships:
        feide_group_memberships = memberships[group_feide_id]
        print("\n" + group_feide_id)
        print("------------------------------------------------")
        group = models.Group.objects.filter(feide_id__exact=group_feide_id).first()
        if not group:
            print("  🚷Group not found in database")
            continue
        # Import teachers
        teachers = feide_group_memberships.get('teachers', [])
        print("Teachers:", len(teachers))
        for teacher in teachers:
            user = models.User.objects.filter(feide_id__exact=teacher['feide_id']).first()
            if user:
                print("  User allready exists")
            else:
                user = models.User.objects.create(
                    name=teacher['name'],
                    feide_id=teacher['feide_id'],
                    email=teacher['email'],
                    maintained_at=timezone.now(),
                )
                user.save()
                print("  User created!", user.email)
            ensure_membership(user, group, teacher_role)

        # Import students
        students = feide_group_memberships.get('students', [])
        print("Students:", len(students))
        for student in students:
            user = models.User.objects.filter(feide_id__exact=student['feide_id']).first()
            if user:
                print("  User allready exists")
            else:
                user = models.User.objects.create(
                    name=student['name'],
                    feide_id=student['feide_id'],
                    email=student['email'],
                    maintained_at=timezone.now(),
                )
                user.save()
                print("  User created!", user.email)
            ensure_membership(user, group, student_role)

    print("✅ import_users_to_db")

if __name__ == "__main__":
    import_users_to_db()
