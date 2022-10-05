# Generated by Django 3.2.12 on 2022-06-30 22:10

from django.db import migrations, models
import django.db.models.deletion
import utils.postgres.managers


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0005_datastore_interval'),
    ]

    operations = [
        migrations.CreateModel(
            name='TableUsageExists',
            fields=[
                ('id', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'definitions_table_usage_exists',
            },
        ),
        migrations.AddField(
            model_name='datastore',
            name='usage_last_synced_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='table',
            name='usage_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='table',
            name='usage_total_queries',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='table',
            name='usage_total_users',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='table',
            name='usage_window',
            field=models.IntegerField(default=None, null=True),
        ),
        migrations.CreateModel(
            name='TableUsage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('execution_date', models.DateField()),
                ('db_schema', models.CharField(max_length=256)),
                ('db_table', models.CharField(max_length=256)),
                ('db_user', models.CharField(max_length=256)),
                ('query_count', models.IntegerField(default=0)),
                ('datastore', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_usage', to='definitions.datastore')),
            ],
            options={
                'db_table': 'definitions_table_usage',
                'unique_together': {('execution_date', 'datastore', 'db_schema', 'db_table', 'db_user')},
                'index_together': {('datastore', 'db_schema', 'db_table')},
            },
            managers=[
                ('objects', utils.postgres.managers.PostgresManager()),
            ],
        ),
    ]