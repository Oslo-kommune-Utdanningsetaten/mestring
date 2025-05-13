import os
import sys
import json
import requests
from dotenv import load_dotenv

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from mastery import models

def ensure_roles_exist():
    """
    Ensure that the roles 'teacher' and 'student' exist in the database.
    If they do not exist, create them.
    """
    teacher_role, _ = models.Role.objects.get_or_create(name='teacher')
    student_role, _ = models.Role.objects.get_or_create(name='student')
    return teacher_role, student_role

# Create a new subject if it doesn't exist
def ensure_membership(user, group, role):
    """
    Ensure that a user is a member of a group with the specified role.
    If the user is not already a member, create the membership.
    """
    user_group, created = models.UserGroup.objects.get_or_create(user=user, group=group, role=role)
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
                )
                user.save()
                print("  User created!", user.email)
            ensure_membership(user, group, student_role)

    print("✅ import_users_to_db")

if __name__ == "__main__":
    import_users_to_db()
