# -*- coding: utf-8 -*-
from django.db import models

from app.authentication.models import Workspace, User
from app.integrations.registry import AVAILABLE_INTEGRATIONS, find_integration

from utils.encrypt.fields import EncryptedCharField
from utils.mixins.models import StringPrimaryKeyModel, TimestampedModel


class IntegrationConfig(StringPrimaryKeyModel, TimestampedModel):
    """Integration configuration for a workspace.
    """
    INTEGRATION_CHOICES = [
        (integration.id, integration.name) for integration in AVAILABLE_INTEGRATIONS
    ]

    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='integrations',
    )

    integration = models.CharField(max_length=32, choices=INTEGRATION_CHOICES)
    displayable = models.CharField(max_length=140)

    auth = EncryptedCharField(max_length=2056, null=False, blank=False)
    meta = models.JSONField(default=dict)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'integration_config'
        unique_together = [
            ('workspace', 'integration', 'displayable')
        ]

    @property
    def integration_handler(self):
        return find_integration(self.integration).handler
