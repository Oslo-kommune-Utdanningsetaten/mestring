from django.db import migrations


def fix_goal_school_references(apps, schema_editor):
    Goal = apps.get_model('mastery', 'Goal')
    Group = apps.get_model('mastery', 'Group')
    Subject = apps.get_model('mastery', 'Subject')
    UserGroup = apps.get_model('mastery', 'UserGroup')
    School = apps.get_model('mastery', 'School')

    for goal in Goal.objects.all():
        correct_school_id = None
        if goal.school_id:
            # All good
            continue

        if goal.group_id:
            # Group goals: get school from group
            group = Group.objects.get(id=goal.group_id)
            correct_school_id = group.school_id
        if not correct_school_id and goal.subject_id:
            # Personal goals: get school from subject
            subject = Subject.objects.get(id=goal.subject_id)
            correct_school_id = subject.owned_by_school_id
        if not correct_school_id and goal.student_id:
            # Personal goals: get school from user group membership
            user_group = UserGroup.objects.filter(
                user_id=goal.student_id
            ).first()
            if user_group:
                group = Group.objects.get(id=user_group.group_id)
                correct_school_id = group.school_id
        if not correct_school_id:
            # Fallback: assign to first school in DB
            correct_school_id = School.objects.first().id

        goal.school_id = correct_school_id
        goal.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0010_goal_school_alter_group_school_alter_group_subject_and_more'),
    ]

    operations = [
        migrations.RunPython(
            fix_goal_school_references,
            reverse_code=migrations.RunPython.noop
        ),
    ]
