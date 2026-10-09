from django.db import migrations


VALUE_INPUT_RENAMES = {
    'toggleComicHorizontal': 'toggleHorizontalComic',
    'sliderArrowHorizontal': 'sliderHorizontalArrow',
    'sliderHorizontal': 'sliderHorizontalStairs',
    'sliderVertical': 'sliderVerticalStairs',
}


def rename_value_input_variants(apps, schema_editor):
    MasterySchema = apps.get_model('mastery', 'MasterySchema')

    for schema in MasterySchema.objects.all():
        if not schema.config:
            continue

        value_input = schema.config.get('value_input')
        if value_input in VALUE_INPUT_RENAMES:
            schema.config['value_input'] = VALUE_INPUT_RENAMES[value_input]
            schema.save(update_fields=['config'])


def reverse_rename_value_input_variants(apps, schema_editor):
    MasterySchema = apps.get_model('mastery', 'MasterySchema')

    reverse_renames = {new: old for old, new in VALUE_INPUT_RENAMES.items()}
    for schema in MasterySchema.objects.all():
        if not schema.config:
            continue

        value_input = schema.config.get('value_input')
        if value_input in reverse_renames:
            schema.config['value_input'] = reverse_renames[value_input]
            schema.save(update_fields=['config'])


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0030_alter_masteryschema_config_and_more'),
    ]

    operations = [
        migrations.RunPython(
            rename_value_input_variants,
            reverse_rename_value_input_variants,
        ),
    ]
