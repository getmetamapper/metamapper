# -*- coding: utf-8 -*-
from app.definitions.models import Schema, Table, Index, Column

from app.revisioner.collectors import ObjectCollector
from app.revisioner.revisioners import get_content_type_for_model


class GenericCreateAction(object):
    """Generic mixin for a bulk CREATED action based on revisions.
    """
    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.revisions = self.run.revisions.created().filter(resource_type_id=self.content_type.id)
        self.num_revisions = self.revisions.count()

    def apply(self):
        """Apply the CREATE action in bulk.
        """
        resources = []

        if not self.num_revisions:
            return []

        for i, revision in enumerate(self.revisions):
            attributes = self.get_attributes(revision)
            if i > 0 and (i % 500 == 0 or i == self.num_revisions):
                self.logger.info(
                    '[{0}] Processed {1} of {2}'.format(self.model_class.__name__, i, self.num_revisions)
                )
            resources.append(
                self.model_class.initialize(**attributes)
            )
        return self.model_class.objects.bulk_create(resources, batch_size=500, ignore_conflicts=True)


class SchemaCreateAction(GenericCreateAction):
    """docstring for SchemaCreateAction
    """
    model_class = Schema

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        defaults = {
            'workspace_id': self.run.workspace_id,
            'datastore_id': self.datastore.id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class TableCreateAction(GenericCreateAction):
    """docstring for TableCreateAction
    """
    model_class = Table

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        schema_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.run.workspace_id,
            'schema_id': schema_id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class ColumnCreateAction(GenericCreateAction):
    """docstring for ColumnCreateAction
    """
    model_class = Column

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        table_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.run.workspace_id,
            'table_id': table_id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class IndexCreateAction(GenericCreateAction):
    """docstring for IndexCreateAction
    """
    model_class = Index

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        metadata = revision.metadata.copy()
        table_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.run.workspace_id,
            'table_id': table_id,
            'created_revision_id': revision.revision_id,
        }
        columns = metadata.pop('columns')
        defaults.update(**metadata)
        return defaults, columns

    def apply(self):
        """Apply the CREATE action in bulk.
        """
        resources = []
        column_cache = {}
        for revision in self.revisions:
            attributes, columns = self.get_attributes(revision)
            instance = self.model_class.initialize(**attributes)
            resources.append(instance)
            column_cache[instance.pk] = columns

        instances = self.model_class.objects.bulk_create(resources, batch_size=500)
        collector = ObjectCollector(
            collection=Column.objects.filter(table__schema__datastore_id=self.datastore.id),
        )
        for instance in instances:
            for c in column_cache.get(instance.pk, []):
                column = collector.find_by(
                    lambda i: i.name.lower() == c['column_name'].lower() and i.table_id == instance.table_id
                )
                instance.index_columns.create(
                    column=column,
                    ordinal_position=c['ordinal_position'],
                    workspace_id=self.run.workspace_id,
                )
        return instances


def get_actions(*args, **kwargs):
    """Retrieve the create action class based on the model name.
    """
    actions = {
        'Schema': SchemaCreateAction,
        'Table': TableCreateAction,
        'Column': ColumnCreateAction,
        'Index': IndexCreateAction,
    }
    return actions.items()
