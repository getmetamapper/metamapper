# -*- coding: utf-8 -*-
import app.notifications.tasks as email
import utils.shortcuts as shortcuts


class EmailAlert(object):
    def __init__(self, alert_rule, check, check_execution, check_error, datastore, workspace):
        self.alert_rule = alert_rule
        self.check = check
        self.check_execution = check_execution
        self.check_error = check_error
        self.datastore = datastore
        self.workspace = workspace

    @property
    def check_name(self):
        return self.check.name

    @property
    def check_timestamp(self):
        return self.check.created_at.strftime('%Y-%m-%dT%H:%M:%S')

    @property
    def selected_execution(self):
        return shortcuts.to_global_id('CheckExecutionType', self.check_execution.id)

    @property
    def recipient_emails(self):
        """list<str>: Emails to deliver notification to.
        """
        return self.alert_rule.channel_config.get('emails', [])

    def meets_criteria(self):
        """bool: Does the scenario match the requirements on the alert rule?
        """
        return True

    def deliver(self):
        """void: Queue notification emails for delivery.
        """
        if not self.meets_criteria():
            return

        for to_email in self.recipient_emails:
            mailer_kwargs = {
                'namespace': 'checks',
                'template': 'check_failed',
                'subject': f'Metamapper check failed: {self.check_name} <{self.check_timestamp}>',
                'to_email': to_email,
                'template_dict': {
                    'check_error': self.check_error,
                    'check_id': self.check.id,
                    'check_name': self.check_name,
                    'datastore_slug': self.datastore.slug,
                    'selected_execution': self.selected_execution,
                    'workspace_slug': self.workspace.slug,
                },
            }
            email.deliver.delay(**mailer_kwargs)
