# Generated by Django 3.0.10 on 2022-03-11 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revisioner', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='run',
            name='fails_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='run',
            name='tasks_count',
            field=models.IntegerField(default=0),
        ),
    ]