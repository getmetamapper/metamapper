# Generated by Django 3.0.7 on 2020-06-28 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_remove_workspace_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='workspace',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='groups',
                to='authentication.Workspace',
            ),
        ),
        migrations.AddField(
            model_name='group',
            name='description',
            field=models.CharField(max_length=180, null=True, blank=True),
        ),
        migrations.RunSQL('ALTER TABLE auth_group DROP CONSTRAINT auth_group_name_key;'),
        migrations.RunSQL('ALTER TABLE auth_group ADD CONSTRAINT auth_group_name_key UNIQUE(name, workspace_id);'),
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
