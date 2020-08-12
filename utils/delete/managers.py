# -*- coding: utf-8 -*-
from utils.delete.querysets import SoftDeletionQuerySet
from utils.postgres.managers import PostgresManager


class SoftDeletionManager(PostgresManager):
    """Handle soft deletion.
    """
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()
