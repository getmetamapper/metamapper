# -*- coding: utf-8 -*-
from django.db import models


class RevisableModel(models.Model):
    """Mixin to make a model revisable.
    """
    created_revision = models.ForeignKey(
        to='revisioner.Revision',
        on_delete=models.DO_NOTHING,
        related_name='+',
        null=True,
        default=None,
    )

    class Meta:
        abstract = True

    @property
    def revisioner_label(self):
        """Decorator function for label in Revisioner output.
        """
        return self.name
