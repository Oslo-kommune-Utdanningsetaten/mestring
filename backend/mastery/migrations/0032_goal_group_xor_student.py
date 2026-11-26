from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0031_rename_value_input_variants'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='goal',
            name='goal_group_or_student',
        ),
        migrations.AddConstraint(
            model_name='goal',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    models.Q(('group__isnull', False), ('student__isnull', True)),
                    models.Q(('group__isnull', True), ('student__isnull', False)),
                    _connector='OR',
                ),
                name='goal_group_xor_student',
            ),
        ),
    ]
