# Generated by Django 3.2.12 on 2022-06-30 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0005_datastore_interval'),
    ]

    operations = [
        migrations.AddField(
            model_name='assetowner',
            name='classification',
            field=models.CharField(choices=[('BUSINESS', 'Business'), ('TECHNICAL', 'Technical')], default='BUSINESS', max_length=12),
        ),
    ]
