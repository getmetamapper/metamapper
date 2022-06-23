# -*- coding: utf-8 -*-
import metamapper.fields as fields
import rest_framework.serializers as serializers

from app.integrations.integration import Integration, Tags


class PagerDutyIntegrationValidator(serializers.Serializer):
    """Required properties of the PagerDuty integration.
    """
    integration_key = fields.CharField(
        label="Integration Key",
        max_length=32,
        allow_blank=False,
        help_text="The 32 character key for an integration on a service.")

    service = fields.CharField(
        label="Service",
        max_length=50,
        help_text="The PagerDuty service this integration key relates to.")


class PagerDutyIntegration(Integration):
    integration_name = "PagerDuty"

    tags = [Tags.ALERTING]

    class Meta:
        auth_keys = ["integration_key"]
        validator = PagerDutyIntegrationValidator
        displayable_key = "service"
