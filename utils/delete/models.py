# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone

from utils.delete.managers import SoftDeletionManager


class SoftDeletionModel(models.Model):
    """Mixin to add soft deletion capabilities.
    """
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        return super(SoftDeletionModel, self).delete()
