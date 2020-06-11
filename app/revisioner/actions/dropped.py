# -*- coding: utf-8 -*-
from app.revisioner.revisioners import KLASS_MAP, get_content_type_for_model


class GenericDropAction(object):
    """Generic mixin for a bulk DROPPED action based on revisions.
    """
    def __init__(self, run, datastore):
        self.run = run
        self.datastore = datastore
        self.model = KLASS_MAP[self.model_name]
        self.content_type = get_content_type_for_model(self.model)
        self.revisions = self.run.revisions.dropped().filter(resource_type=self.content_type)

    def get_resource_ids(self):
        """Retrieve the resource IDs for this cache.
        """
        return self.revisions.values_list('resource_id', flat=True)

    def apply(self):
        """Apply DELETE action to all dropped models.
        """
        response = self.model.objects.filter(id__in=self.get_resource_ids()).delete()
        if isinstance(response, tuple):
            return response[0]
        return response


class SchemaDropAction(GenericDropAction):
    """docstring for SchemaDropAction
    """
    model_name = 'Schema'


class TableDropAction(GenericDropAction):
    """docstring for SchemaDropAction
    """
    model_name = 'Table'


class ColumnDropAction(GenericDropAction):
    """docstring for ColumnDropAction
    """
    model_name = 'Column'


class IndexDropAction(GenericDropAction):
    """docstring for IndexDropAction
    """
    model_name = 'Index'


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
