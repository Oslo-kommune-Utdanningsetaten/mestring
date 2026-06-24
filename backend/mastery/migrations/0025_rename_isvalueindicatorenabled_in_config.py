from django.db import migrations


def rename_is_value_indicator_enabled(apps, schema_editor):
    """
    Rename 'is_value_indicator_enabled' to 'is_mastery_value_visible' in all MasterySchema config fields,
    preserving the existing value.
    """
    MasterySchema = apps.get_model('mastery', 'MasterySchema')

    updated_count = 0
    for schema in MasterySchema.objects.all():
        if schema.config and 'is_value_indicator_enabled' in schema.config:
            schema.config['is_mastery_value_visible'] = schema.config.pop('is_value_indicator_enabled')
            schema.save()
            updated_count += 1

    print(f"Updated {updated_count} mastery schema config(s)")


def reverse_rename_is_value_indicator_enabled(apps, schema_editor):
    """
    Reverse: rename 'is_mastery_value_visible' back to 'is_value_indicator_enabled'.
    """
    MasterySchema = apps.get_model('mastery', 'MasterySchema')

    for schema in MasterySchema.objects.all():
        if schema.config and 'is_mastery_value_visible' in schema.config:
            schema.config['is_value_indicator_enabled'] = schema.config.pop('is_mastery_value_visible')
            schema.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0024_remove_observation_observer'),
    ]

    operations = [
        migrations.RunPython(
            rename_is_value_indicator_enabled,
            reverse_rename_is_value_indicator_enabled,
        ),
    ]
