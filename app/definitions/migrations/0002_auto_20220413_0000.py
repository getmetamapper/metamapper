# Generated by Django 3.2.12 on 2022-04-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datastore',
            name='custom_properties',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='datastore',
            name='extras',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='table',
            name='custom_properties',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='table',
            name='properties',
            field=models.JSONField(default=dict),
        ),
    ]