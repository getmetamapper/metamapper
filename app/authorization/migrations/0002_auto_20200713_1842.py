# Generated by Django 3.0.7 on 2020-06-28 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'),
        ('authentication', '0005_auto_20200706_0214'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AddField(
            model_name='group',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=('workspace_id', 'name',)
        ),
    ]

    def mutate_state(self, project_state, preserve=True):
        """
        This is a workaround that allows to store ``auth``
        migration outside the directory it should be stored.
        """
        app_label = self.app_label
        self.app_label = 'auth'
        state = super(Migration, self).mutate_state(project_state, preserve)
        self.app_label = app_label
        return state

    def apply(self, project_state, schema_editor, collect_sql=False):
        """
        Same workaround as described in ``mutate_state`` method.
        """
        app_label = self.app_label
        self.app_label = 'auth'
        state = super(Migration, self).apply(project_state, schema_editor, collect_sql)
        self.app_label = app_label
        return state
