# -*- coding: utf-8 -*-
import app.notifications.tasks as email


class EmailAlert(object):
    def __init__(self, alert_rule, check, error, datastore, workspace):
        self.alert_rule = alert_rule
        self.check = check
        self.error = error
        self.datastore = datastore
        self.workspace = workspace

    @property
    def check_name(self):
        return self.check.name

    @property
    def check_timestamp(self):
        return self.check.created_at.strftime('%Y-%m-%dT%H:%M:%S')

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
                    'check_id': self.check.id,
                    'check_name': self.check_name,
                    'datastore_slug': self.datastore.slug,
                    'workspace_slug': self.workspace.slug,
                    'error': self.error,
                },
            }
            email.deliver.delay(**mailer_kwargs)
