# Generated by Django 3.0.10 on 2022-03-09 19:19

import app.audit.managers
from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_object_id', models.CharField(blank=True, db_index=True, help_text='The object that the action (in)directly affects', max_length=255, null=True)),
                ('action_object_object_id', models.CharField(blank=True, db_index=True, help_text='The object that the action was made on', max_length=255, null=True)),
                ('verb', models.CharField(db_index=True, max_length=255)),
                ('extras', django.contrib.postgres.fields.jsonb.JSONField(default=dict, help_text='Additional metadata related to the change')),
                ('old_values', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('new_values', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now)),
                ('action_object_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='action_object', to='contenttypes.ContentType')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL)),
                ('target_content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='target', to='contenttypes.ContentType')),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='authentication.Workspace')),
            ],
            options={
                'ordering': ('-timestamp',),
            },
            managers=[
                ('objects', app.audit.managers.ActionManager()),
            ],
        ),
    ]
