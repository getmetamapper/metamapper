# -*- coding: utf-8 -*-
import metamapper.fields as fields
import rest_framework.serializers as serializers

from app.integrations.integration import Integration, Tags


class SlackIntegrationValidator(serializers.Serializer):
    """Required properties of the Slack integration.
    """
    token = fields.CharField(
        label="Token",
        max_length=128,
        help_text="The authentication token with required scopes.")

    workspace = fields.CharField(
        label="Workspace",
        max_length=50,
        help_text="The Slack service this authentication token relates to.")

    bot_name = fields.CharField(
        label="Bot Name",
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=20,
        help_text="The name used when publishing messages.")

    icon_url = fields.CharField(
        label="Icon URL",
        required=False,
        allow_null=True,
        allow_blank=True,
        max_length=None,
        help_text="The url of the icon to appear beside your bot (32px png), leave empty for none.")


class SlackIntegration(Integration):
    integration_name = "Slack"

    tags = [Tags.ALERTING]

    class Meta:
        auth_keys = ["token"]
        validator = SlackIntegrationValidator
        displayable_key = "workspace"
