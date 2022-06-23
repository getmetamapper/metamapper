# -*- coding: utf-8 -*-
import metamapper.fields as fields

from app.checks.alerts.base import Alert, Validator
from app.notifications import tasks as email


class EmailAlertConfigValidator(Validator):
    """Validate the configuration struct for an Email alert channel.
    """
    emails = fields.EmailsField(
        label="Emails",
        allow_empty=False,
        help_text="Where we should send the alert.")


class EmailAlert(Alert):
    """Alert via email on check failure.
    """
    class Meta:
        name = "Email"
        integration = "EMAIL"
        validator = EmailAlertConfigValidator

    def send(self):
        """void: Send alert via Email channel.
        """
        for to_email in self.recipient_emails:
            mailer_kwargs = {
                "namespace": "checks",
                "template": "check_failed",
                "subject": f"Metamapper check failed: {self.check_name} <{self.check_timestamp}>",
                "to_email": to_email,
                "template_dict": {
                    "check_error": self.check_error,
                    "check_name": self.check_name,
                    "check_url": self.check_url,
                    "workspace_slug": self.workspace.slug,
                },
            }
            email.deliver.delay(**mailer_kwargs)
