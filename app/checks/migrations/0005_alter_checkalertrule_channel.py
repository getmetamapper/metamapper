# Generated by Django 3.2.12 on 2022-06-18 03:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checks', '0004_alter_checkexpectationresult_expectation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkalertrule',
            name='channel',
            field=models.CharField(choices=[('EMAIL', 'Email'), ('PAGERDUTY', 'PagerDuty'), ('SLACK', 'Slack')], max_length=15),
        ),
    ]
