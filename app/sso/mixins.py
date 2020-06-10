# -*- coding: utf-8 -*-
from django.db import models
from app.sso.models import SSOConnection


class SSOTenantModel(models.Model):
    """Mixin to add SSO tenant capabilities.
    """
    active_sso = models.ForeignKey(
        to=SSOConnection,
        null=True,
        related_name='+',
        on_delete=models.DO_NOTHING,
    )

    class Meta:
        abstract = True

    @property
    def is_sso_enabled(self):
        return self.active_sso_id is not None and self.active_sso.is_enabled

    @property
    def is_sso_forced(self):
        return self.is_sso_enabled
