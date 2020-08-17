# -*- coding: utf-8 -*-
from django.core.paginator import Paginator

from app.definitions.models import Schema, Table, Index, Column
from app.revisioner.collectors import ObjectCollector
from app.revisioner.revisioners import get_content_type_for_model

from utils.postgres.types import ConflictAction


class GenericCreateAction(object):
    """Generic mixin for a bulk CREATED action based on revisions.
    """
    conflict_target = None

    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.workspace_id = self.run.workspace_id
        self.revisions = (
            self.run.revisions
                    .created()
                    .filter(resource_type_id=self.content_type.id)
                    .order_by('created_at')
        )

    def bulk_insert(self, rows):
        """Perform a bulk INSERT and ignore duplicate records.
        """
        self.model_class.objects.on_conflict(self.conflict_target, ConflictAction.NOTHING).bulk_insert(rows)

    def apply(self, batch_size=2000):
        """Apply the CREATE action in bulk.
        """
        paginator = Paginator(self.revisions, batch_size)

        for page_num in paginator.page_range:
            page = paginator.get_page(page_num)
            data = [
                self.get_attributes(revision) for revision in page.object_list
            ]

            if len(data):
                self.bulk_insert(data)

            self.logger.info(
                '[{0}] Created {1} of {2}'.format(self.model_class.__name__, page.end_index(), paginator.count)
            )


class SchemaCreateAction(GenericCreateAction):
    """docstring for SchemaCreateAction
    """
    model_class = Schema

    conflict_target = ['datastore_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        defaults = {
            'workspace_id': self.workspace_id,
            'datastore_id': self.datastore.id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class TableCreateAction(GenericCreateAction):
    """docstring for TableCreateAction
    """
    model_class = Table

    conflict_target = ['schema_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        schema_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.workspace_id,
            'schema_id': schema_id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class ColumnCreateAction(GenericCreateAction):
    """docstring for ColumnCreateAction
    """
    model_class = Column

    conflict_target = ['table_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        table_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.workspace_id,
            'table_id': table_id,
            'created_revision_id': revision.revision_id,
        }
        defaults.update(**revision.metadata)
        return defaults


class IndexCreateAction(GenericCreateAction):
    """docstring for IndexCreateAction
    """
    model_class = Index

    conflict_target = ['table_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        metadata = revision.metadata.copy()
        table_id = revision.parent_instance.id
        defaults = {
            'workspace_id': self.workspace_id,
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
            instance = self.model_class(**attributes)
            resources.append(instance)
            column_cache[instance.name] = columns

        instances = self.model_class.objects.bulk_create(resources, batch_size=500)
        collector = ObjectCollector(
            Column.objects.filter(table__schema__datastore_id=self.datastore.id).only('pk', 'object_id', 'name')
        )
        for instance in instances:
            for c in column_cache.get(instance.pk, []):
                column = collector.find_by(
                    lambda i: i.name.lower() == c['column_name'].lower() and i.table_id == instance.table_id
                )
                instance.index_columns.create(
                    column=column,
                    ordinal_position=c['ordinal_position'],
                    workspace_id=self.workspace_id,
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
