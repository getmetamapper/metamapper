# -*- coding: utf-8 -*-
import metamapper.fields as fields

from app.checks.alerts.base import Alert, Validator
from app.integrations.pagerduty.client import PagerDutyClient


class PagerDutyAlertConfigValidator(Validator):
    """Validate the configuration struct for an PagerDuty alert channel.
    """
    integration_id = fields.IntegrationField(
        label="Service",
        max_length=40,
        help_text="Which PagerDuty service we should send the alert to.")

    severity = fields.ChoiceField(
        label="Severity",
        choices=["critical", "error", "warning", "info"],
        help_text="How important this alert is.")


class PagerDutyAlert(Alert):
    """Alert via PagerDuty on check failure.
    """
    class Meta:
        name = "PagerDuty"
        integration = "PAGERDUTY"
        validator = PagerDutyAlertConfigValidator

    @property
    def integration_id(self):
        return self.alert_rule.channel_config["integration_id"]

    @property
    def severity(self):
        return self.alert_rule.channel_config["severity"]

    @property
    def dedup_key(self):
        return "%s-%s" % (self.check.id, self.check_execution.epoch)

    def get_integration_config(self):
        return self.workspace.integrations.get(id=self.integration_id, integration="PAGERDUTY")

    def send(self):
        """void: Send alert via PagerDuty channel.
        """
        integration_config = self.get_integration_config()
        integration = integration_config.integration_handler

        api_kwargs = {
            "source": "Metamapper",
            "summary": f"Metamapper check failed: {self.check_name} <{self.check_timestamp}>",
            "severity": self.severity,
            "href": self.check_url,
            "component": "%s (%s)" % (self.datastore.name, self.datastore.slug),
            "group": "%s (%s)" % (self.workspace.name, self.workspace.slug),
            "dedup_key": self.dedup_key,
        }

        client = PagerDutyClient(integration.auth_out(integration_config))
        client.send_trigger(**api_kwargs)
