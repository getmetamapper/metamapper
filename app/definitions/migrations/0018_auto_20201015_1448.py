# Generated by Django 3.0.8 on 2020-10-15 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0017_auto_20200906_0221'),
    ]

    operations = [
        migrations.AlterField(
            model_name='column',
            name='short_desc',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='table',
            name='short_desc',
            field=models.TextField(blank=True, null=True),
        ),
    ]
