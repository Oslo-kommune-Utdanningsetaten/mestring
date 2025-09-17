from mastery import models
from django.db import connection
import django
import os
import sys
from dotenv import load_dotenv
from pyexcel_xlsx import get_data
from django.utils import timezone


script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
load_dotenv(os.path.join(project_root, '.env'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()


def ensure_test_school():
    """
    Ensure that a test school exists in the database.
    If it does not exist, create it.
    """
    school_id = 'kakrafoonorg'
    school = models.School.objects.filter(id=school_id).first()
    if not school:
        print("Creating test school:", school_id)
        school = models.School.objects.create(
            display_name='Kakrafoon barneskole',
            short_name='kak',
            id='kakrafoonorg',
            maintained_at=timezone.now(),
            feide_id='fc:org:feide.osloskolen.no:unit:NO987654321',
            org_number='NO987654321',
            is_service_enabled=True,
        )
        school.save()
    return school


def ensure_mastery_schema_exists():
    title = 'Mestringstrappa'
    mastery_schema = models.MasterySchema.objects.filter(title=title).first()
    if not mastery_schema:
        print("Creating default mastery_schema:", title)
        mastery_schema = models.MasterySchema.objects.create(
            title=title,
            description='Mestring angitt med fem nivåer, fra "aldri" til "mestrer".',
            maintained_at=timezone.now(),
            config={
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
    """Ensure that neccessary roles exist"""
    teacher_role = models.Role.objects.filter(name="teacher").first()
    student_role = models.Role.objects.filter(name="student").first()
    admin_role = models.Role.objects.filter(name="admin").first()
    staff_role = models.Role.objects.filter(name="staff").first()

    if not teacher_role:
        teacher_role = models.Role.objects.create(
            name="teacher", maintained_at=timezone.now()
        )
    if not student_role:
        student_role = models.Role.objects.create(
            name="student", maintained_at=timezone.now()
        )
    if not admin_role:
        admin_role = models.Role.objects.create(
            name="admin", maintained_at=timezone.now()
        )
    if not staff_role:
        staff_role = models.Role.objects.create(
            name="staff", maintained_at=timezone.now()
        )

    return teacher_role, student_role, admin_role, staff_role


def objects_from_sheet(sheet, field_names):
    objects = []
    sheet_field_names = sheet[0]
    for row in sheet[1:]:
        obj = {}
        for index, field_value in enumerate(row):
            field_name = sheet_field_names[index]
            if field_name in field_names:
                if field_value is None or field_value == '':
                    field_value = None
                obj[field_name] = field_value
            else:
                print(f"🚫Warning: Field '{field_name}' not in field_names, skipping.")
                continue
        if bool(obj):
            objects.append(obj)
    return objects


def run_import():
    excel_file_path = os.path.join(script_dir, 'data', 'data_for_import.xlsx')
    excel_file_sheets = get_data(excel_file_path)
    teacher_role, student_role, _, _ = ensure_roles_exist()

    # import subjects from kakrafoon.subject sheet
    if 'kakrafoon.subject' in excel_file_sheets:
        print("Importing subjects...")
        sheet = excel_file_sheets['kakrafoon.subject']
        field_names = ['id', 'display_name', 'owned_by_school']
        subject_dicts = objects_from_sheet(sheet, field_names)
        results = []
        for subject_dict in subject_dicts:
            school = models.School.objects.filter(id__exact=subject_dict['owned_by_school']).first()
            defaults = {'maintained_at': timezone.now()}
            for k, v in subject_dict.items():
                if k == 'id':
                    continue
                elif k == 'owned_by_school':
                    defaults['owned_by_school'] = school
                else:
                    defaults[k] = v
            subject, created = models.Subject.objects.get_or_create(id=subject_dict['id'], defaults=defaults)
            results.append({'object': subject, 'created': created})
        print("Subjects imported:", len(results))

    # import groups from kakrafoon.group sheet
    if 'kakrafoon.group' in excel_file_sheets:
        print("Importing groups...")
        sheet = excel_file_sheets['kakrafoon.group']
        field_names = ['id', 'feide_id', 'display_name', 'type',
                       'subject_id', 'school_id', 'valid_from', 'valid_to']
        group_dicts = objects_from_sheet(sheet, field_names)
        results = []
        for group_dict in group_dicts:
            school = models.School.objects.filter(id__exact=group_dict['school_id']).first()
            subject = models.Subject.objects.filter(id__exact=group_dict['subject_id']).first(
            ) if group_dict['subject_id'] is not None else None
            defaults = {'maintained_at': timezone.now()}
            for k, v in group_dict.items():
                if k == 'id':
                    continue
                elif k == 'school_id' and school:
                    defaults['school'] = school
                elif k == 'subject_id' and subject is not None:
                    defaults['subject'] = subject
                else:
                    defaults[k] = v
            group, created = models.Group.objects.get_or_create(id=group_dict['id'], defaults=defaults)
            results.append({'object': group, 'created': created})
        print("Groups imported:", len(results))

    # import group members from kakrafoon.member sheet
    if 'kakrafoon.member' in excel_file_sheets:
        print("Importing members...")
        sheet = excel_file_sheets['kakrafoon.member']
        field_names = ['id', 'user_feide_id', 'role', 'group_feide_id', 'name']
        member_dicts = objects_from_sheet(sheet, field_names)
        results = []
        for member_dict in member_dicts:
            # maybe create the user
            user_email = member_dict['user_feide_id'].split(':')[1].replace('@feide.', '@')
            user, created = models.User.objects.get_or_create(
                feide_id=member_dict['user_feide_id'],
                defaults={'name': member_dict['name'], 'email': user_email, 'maintained_at': timezone.now()})
            group = models.Group.objects.filter(feide_id__exact=member_dict['group_feide_id']).first()
            role = teacher_role if member_dict['role'] == 'teacher' else student_role
            defaults = {'maintained_at': timezone.now()}
            for k, v in member_dict.items():
                if k == 'id':
                    continue
                elif k == 'user_feide_id' and user:
                    defaults['user'] = user
                elif k == 'group_feide_id' and group:
                    defaults['group'] = group
                elif k == 'role':
                    defaults['role'] = role
            user_group, created = models.UserGroup.objects.get_or_create(
                id=member_dict['id'], defaults=defaults)
            results.append({'object': user_group, 'created': created})
        print("UserGroups imported:", len(results))

    # import goals from kakrafoon.goal sheet
    if 'kakrafoon.goal' in excel_file_sheets:
        print("Importing goals...")
        sheet = excel_file_sheets['kakrafoon.goal']
        field_names = ['id', 'title', 'subject_id', 'student_feide_id']  # ONLY IMPORTING STUDENT GOALS!
        goal_dicts = objects_from_sheet(sheet, field_names)
        results = []
        schema = ensure_mastery_schema_exists()
        for goal_dict in goal_dicts:
            subject = models.Subject.objects.filter(id__exact=goal_dict['subject_id']).first()
            student = models.User.objects.filter(feide_id__exact=goal_dict['student_feide_id']).first()
            defaults = {'maintained_at': timezone.now(), 'mastery_schema': schema}
            for k, v in goal_dict.items():
                if k == 'id':
                    continue
                elif k == 'student_feide_id':
                    defaults['student'] = student
                elif k == 'subject_id':
                    defaults['subject'] = subject
                else:
                    defaults[k] = v
            goal, created = models.Goal.objects.get_or_create(id=goal_dict['id'], defaults=defaults)
            results.append({'object': goal, 'created': created})
        print("Goals imported:", len(results))

    # import observations from kakrafoon.observation sheet
    if 'kakrafoon.observation' in excel_file_sheets:
        print("Importing observations...")
        sheet = excel_file_sheets['kakrafoon.observation']
        field_names = ['id', 'observed_at', 'mastery_value', 'mastery_description',
                       'feedforward', 'goal_id', 'student_feide_id', 'observer_feide_id']
        observation_dicts = objects_from_sheet(sheet, field_names)
        results = []
        for observation_dict in observation_dicts:
            student = models.User.objects.filter(feide_id__exact=observation_dict['student_feide_id']).first()
            observer = models.User.objects.filter(
                feide_id__exact=observation_dict['observer_feide_id']).first()
            goal = models.Goal.objects.filter(id=observation_dict['goal_id']).first()
            defaults = {'maintained_at': timezone.now()}
            for k, v in observation_dict.items():
                if k == 'id':
                    continue
                elif k == 'student_feide_id':
                    defaults['student'] = student
                elif k == 'observer_feide_id':
                    defaults['observer'] = observer
                elif k == 'goal_id':
                    defaults['goal'] = goal
                else:
                    defaults[k] = v
            observation, created = models.Observation.objects.get_or_create(
                id=observation_dict['id'], defaults=defaults)
            results.append({'object': observation, 'created': created})
        print("Observations imported:", len(results))

    print("Excel import all done")


if __name__ == '__main__':
    ensure_test_school()
    run_import()
