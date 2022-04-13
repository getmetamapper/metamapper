# Generated by Django 3.0.10 on 2022-04-01 21:16

from django.db import migrations, models
import django.db.models.deletion
import utils.encrypt.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authentication', '0001_initial'),
        ('authorization', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApiToken',
            fields=[
                ('id', models.CharField(db_index=True, editable=False, max_length=40, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=60)),
                ('is_enabled', models.BooleanField(default=True)),
                ('token', utils.encrypt.fields.EncryptedCharField(max_length=32)),
                ('last_used_at', models.DateTimeField(default=None, null=True)),
                ('workspace', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='api_tokens', to='authentication.Workspace')),
            ],
            options={
                'db_table': 'api_token',
                'unique_together': {('workspace', 'name')},
            },
        ),
    ]