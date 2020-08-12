# -*- coding: utf-8 -*-
from django.utils import timezone

from utils.postgres.querysets import PostgresQuerySet


class SoftDeletionQuerySet(PostgresQuerySet):
    """Queryset for SoftDeletionManager.
    """
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)
