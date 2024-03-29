# Generated by Django 3.2.12 on 2022-04-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customfields', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfield',
            name='field_type',
            field=models.CharField(choices=[('USER', 'User'), ('TEXT', 'Text'), ('ENUM', 'Enum'), ('GROUP', 'Group'), ('MULTI', 'Multiselect')], max_length=30),
        ),
        migrations.AlterField(
            model_name='customfield',
            name='validators',
            field=models.JSONField(default=dict),
        ),
    ]
