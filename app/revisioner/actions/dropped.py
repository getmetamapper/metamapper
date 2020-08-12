# -*- coding: utf-8 -*-
from app.definitions.models import Schema, Table, Column, Index
from app.revisioner.revisioners import get_content_type_for_model

from django.db.models import IntegerField
from django.db.models.functions import Cast


class GenericDropAction(object):
    """Generic mixin for a bulk DROPPED action based on revisions.
    """
    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.revisions = self.run.revisions.dropped().filter(resource_type=self.content_type)

    def get_resource_ids(self):
        """Retrieve the resource IDs for this cache.
        """
        return self.revisions.annotate(as_int=Cast('resource_id', IntegerField())).values_list('as_int', flat=True)

    def apply(self):
        """Apply DELETE action to all dropped models.
        """
        response = self.model_class.objects.filter(id__in=self.get_resource_ids()).delete()
        if isinstance(response, tuple):
            return response[0]
        return response


class SchemaDropAction(GenericDropAction):
    """docstring for SchemaDropAction
    """
    model_class = Schema


class TableDropAction(GenericDropAction):
    """docstring for SchemaDropAction
    """
    model_class = Table


class ColumnDropAction(GenericDropAction):
    """docstring for ColumnDropAction
    """
    model_class = Column


class IndexDropAction(GenericDropAction):
    """docstring for IndexDropAction
    """
    model_class = Index


def get_actions(*args, **kwargs):
    """Retrieve the drop action class based on the model name.
    """
    actions = {
        'Schema': SchemaDropAction,
        'Table': TableDropAction,
        'Column': ColumnDropAction,
        'Index': IndexDropAction,
    }
    return actions.items()
