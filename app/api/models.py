# -*- coding: utf-8 -*-
from django.db import models
from base64 import b64encode

from app.authentication.models import Workspace
from utils.encrypt.fields import EncryptedCharField
from utils.mixins.models import StringPrimaryKeyModel, TimestampedModel


class ApiToken(StringPrimaryKeyModel, TimestampedModel):
    """Represents an authorization token for accessing the Metamapper API.
    """
    workspace = models.ForeignKey(
        to=Workspace,
        on_delete=models.CASCADE,
        related_name='api_tokens',
    )

    name = models.CharField(max_length=60)

    is_enabled = models.BooleanField(default=True)

    token = EncryptedCharField(max_length=32, null=False, blank=False)

    class Meta:
        db_table = 'api_token'
        unique_together = ('workspace', 'name',)

    def get_secret(self):
        return b64encode(':'.join([self.id, self.token]).encode('utf-8')).decode()
