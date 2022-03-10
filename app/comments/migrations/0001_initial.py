# Generated by Django 3.0.10 on 2022-03-09 19:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.mixins.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0003_workspace_active_sso'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.CharField(db_index=True, editable=False, max_length=40, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('num_vote_up', models.PositiveIntegerField(db_index=True, default=0)),
                ('num_vote_down', models.PositiveIntegerField(db_index=True, default=0)),
                ('object_id', models.IntegerField()),
                ('html', models.TextField()),
                ('text', models.TextField()),
                ('pinned_at', models.DateTimeField(default=None, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='child_comments', to='comments.Comment')),
                ('pinned_by', models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='authentication.Workspace')),
            ],
            options={
                'db_table': 'comments',
                'index_together': {('content_type', 'object_id')},
            },
            bases=(utils.mixins.models.AuditableModel, models.Model),
        ),
    ]
