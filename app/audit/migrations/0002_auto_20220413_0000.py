# Generated by Django 3.2.12 on 2022-04-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('audit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='extras',
            field=models.JSONField(default=dict, help_text='Additional metadata related to the change'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='new_values',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='activity',
            name='old_values',
            field=models.JSONField(default=dict),
        ),
    ]
