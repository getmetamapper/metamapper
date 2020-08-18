# -*- coding: utf-8 -*-
from django.db import models


class RevisableModel(models.Model):
    """Mixin to make a model revisable.
    """
    created_revision_id = models.CharField(
        max_length=40,
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
