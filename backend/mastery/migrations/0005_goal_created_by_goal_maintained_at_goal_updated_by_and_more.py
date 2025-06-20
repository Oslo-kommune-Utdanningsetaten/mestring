# Generated by Django 4.2.20 on 2025-06-17 08:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mastery', '0004_remove_goal_mastery_schema_goal_mastery_schema_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='goal',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='goal',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='group',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='group',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='masteryschema',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='masteryschema',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='masteryschema',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='observation',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='observation',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='observation',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='role',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='role',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='role',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='school',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='school',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='school',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='situation',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='situation',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='situation',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='status',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='status',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='status',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='subject',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='subject',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='subject',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='user',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='user',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='created_%(class)s_set', to='mastery.user'),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='maintained_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='usergroup',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_%(class)s_set', to='mastery.user'),
        ),
    ]
