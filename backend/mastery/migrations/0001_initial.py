# Generated by Django 4.2.20 on 2025-05-28 06:00

from django.db import migrations, models
import django.db.models.deletion
import mastery.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(null=True)),
                ('mastery_schema', models.JSONField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('feide_id', models.CharField(max_length=200, unique=True)),
                ('display_name', models.CharField(max_length=200)),
                ('type', models.CharField(max_length=200)),
                ('valid_from', models.DateTimeField(null=True)),
                ('valid_to', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='School',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('feide_id', models.CharField(max_length=200, unique=True)),
                ('display_name', models.CharField(max_length=200)),
                ('short_name', models.CharField(max_length=10, null=True)),
                ('org_number', models.CharField(max_length=50)),
                ('owner', models.CharField(max_length=200, null=True)),
                ('is_service_enabled', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Situation',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(null=True)),
                ('happens_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('feide_id', models.CharField(max_length=200, unique=True)),
                ('email', models.CharField(max_length=200)),
                ('last_activity_at', models.DateTimeField(null=True)),
                ('disabled_at', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserGroup',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_groups', to='mastery.group')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mastery.role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_groups', to='mastery.user')),
            ],
            options={
                'unique_together': {('user', 'group', 'role')},
            },
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(null=True, related_name='members', through='mastery.UserGroup', to='mastery.group'),
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('display_name', models.CharField(max_length=200)),
                ('short_name', models.CharField(max_length=200)),
                ('grep_code', models.CharField(max_length=200, null=True)),
                ('grep_group_code', models.CharField(max_length=200, null=True)),
                ('maintened_by_school', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='subjects', to='mastery.school')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('estimated_at', models.DateTimeField(null=True)),
                ('mastery_value', models.IntegerField(null=True)),
                ('mastery_description', models.TextField(null=True)),
                ('feedforward', models.TextField(null=True)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mastery.user')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mastery.subject')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Observation',
            fields=[
                ('id', models.CharField(default=mastery.models.generate_nanoid, editable=False, max_length=12, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mastery_value', models.IntegerField(null=True)),
                ('mastery_description', models.TextField(null=True)),
                ('feedforward', models.TextField(null=True)),
                ('observed_at', models.DateTimeField(null=True)),
                ('is_private', models.BooleanField(default=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='mastery.goal')),
                ('observer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='observations_performed', to='mastery.user')),
                ('situation', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='mastery.situation')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='observations_received', to='mastery.user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='group',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='groups', to='mastery.school'),
        ),
        migrations.AddField(
            model_name='group',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='mastery.subject'),
        ),
        migrations.AddField(
            model_name='goal',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='mastery.group'),
        ),
        migrations.AddField(
            model_name='goal',
            name='previous_goal',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='mastery.goal'),
        ),
        migrations.AddField(
            model_name='goal',
            name='student',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='mastery.user'),
        ),
        migrations.AddField(
            model_name='goal',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to='mastery.subject'),
        ),
        migrations.AddConstraint(
            model_name='goal',
            constraint=models.CheckConstraint(check=models.Q(('group__isnull', False), ('student__isnull', False), _connector='OR'), name='goal_group_or_student'),
        ),
    ]
