# -*- coding: utf-8 -*-
import metamapper.fields as fields
import rest_framework.serializers as serializers

from app.checks.alerts.base import Alert, Validator
from app.integrations.slack.client import SlackClient


class SlackAlertConfigValidator(Validator):
    """Validate the configuration struct for an Slack alert channel.
    """
    integration_id = fields.IntegrationField(
        label="Workspace",
        max_length=40,
        help_text="Which Slack workspace we should send the alert to.")

    channel = fields.CharField(
        label="Channel",
        max_length=80,
        help_text="The Slack channel to send the alert to.")

    severity = fields.ChoiceField(
        label="Severity",
        choices=["critical", "error", "warning", "info"],
        help_text="How important this alert is.")

    def validate_channel(self, channel):
        """Must have correct beginning character.
        """
        if channel.startswith("@") or channel.startswith("#"):
            return channel
        raise serializers.ValidationError("Channel must be a valid channel or username.")


class SlackAlert(Alert):
    """Alert via Slack on check failure.
    """
    class Meta:
        name = "Slack"
        integration = "SLACK"
        validator = SlackAlertConfigValidator

    @property
    def integration_id(self):
        return self.alert_rule.channel_config["integration_id"]

    @property
    def channel(self):
        return self.alert_rule.channel_config["channel"]

    @property
    def severity(self):
        return self.alert_rule.channel_config["severity"]

    @property
    def severity_color(self):
        mapping = {
            "info": "#C8C8C8",
            "warning": "#FFD30D",
            "error": "#B71F1F",
            "critical": "#B71F1F",
        }
        return mapping.get(self.severity, mapping["critical"])

    @property
    def default_username(self):
        return "Metamapper"

    @property
    def default_icon_url(self):
        return "https://avatars.githubusercontent.com/u/47652283?s=200&v=4"

    def get_integration_config(self):
        return self.workspace.integrations.get(id=self.integration_id, integration="SLACK")

    def send(self):
        """void: Send alert via Slack channel.
        """
        integration_config = self.get_integration_config()
        integration = integration_config.integration_handler

        api_kwargs = {
            "channel": self.channel,
            "username": integration_config.meta.get("bot_name") or self.default_username,
            "icon_url": integration_config.meta.get("icon_url") or self.default_icon_url,
            "attachments": [
                {
                    "color": self.severity_color,
                    "title": f"Metamapper check failed: {self.check_name} <{self.check_timestamp}>",
                    "title_link": self.check_url,
                    "text": self.check_error,
                    "fields": [
                        {
                            "title": "Datastore",
                            "value": self.datastore.name,
                            "short": False
                        },
                        {
                            "title": "Severity",
                            "value": self.severity,
                            "short": False
                        },
                    ],
                    "footer": self.workspace.slug,
                    "ts": int(self.check.created_at.timestamp()),
                }
            ]
        }

        client = SlackClient(integration.auth_out(integration_config))
        client.post("/chat.postMessage", data=api_kwargs)
