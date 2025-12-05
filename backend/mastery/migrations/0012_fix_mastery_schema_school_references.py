from django.db import migrations


def fix_mastery_schema_school_references(apps, schema_editor):
    MasterySchema = apps.get_model('mastery', 'MasterySchema')
    School = apps.get_model('mastery', 'School')

    for schema in MasterySchema.objects.all():
        if schema.school_id:
            # All good
            continue

        schema.school_id = School.objects.first().id
        schema.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0011_fix_goal_school_references'),
    ]

    operations = [
        migrations.RunPython(
            fix_mastery_schema_school_references,
            reverse_code=migrations.RunPython.noop
        ),
    ]
