# Generated by Django 3.2.12 on 2022-04-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sso', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ssoconnection',
            name='extras',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='ssoidentity',
            name='metadata',
            field=models.JSONField(default=dict),
        ),
    ]
