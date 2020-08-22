# -*- coding: utf-8 -*-
from django.core.paginator import Paginator
from django.db.models import IntegerField
from django.db.models.functions import Cast

from app.definitions.models import Schema, Table, Column, Index
from utils.contenttypes import get_content_type_for_model


class GenericDropAction(object):
    """Generic mixin for a bulk DROPPED action based on revisions.
    """
    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.workspace_id = self.run.workspace_id
        self.revisions = (
            self.run.revisions
                    .dropped()
                    .filter(resource_type=self.content_type)
                    .annotate(as_int=Cast('resource_id', IntegerField()))
                    .order_by('created_at')
        )

    def apply(self, batch_size=1000):
        """Apply DELETE action to all dropped models.
        """
        paginator = Paginator(self.revisions, batch_size)

        for page_num in paginator.page_range:
            page = paginator.get_page(page_num)
            data = page.object_list.values_list('as_int', flat=True)

            self.logger.info(
                '[{0}] Dropped {1} of {2}'.format(self.model_class.__name__, page.end_index(), paginator.count)
            )

            self.model_class.objects.filter(id__in=data).delete()


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
