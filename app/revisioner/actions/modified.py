# -*- coding: utf-8 -*-
from django.core.paginator import Paginator

from app.definitions.models import Schema, Table, Column, Index, IndexColumn
from app.revisioner.collectors import ObjectCollector
from app.revisioner.revisioners import get_content_type_for_model

from utils.postgres.types import ConflictAction


class GenericModifyAction(object):
    """Generic mixin for a bulk MODIFIED action based on revisions.
    """
    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.workspace_id = self.run.workspace_id
        self.collector = self.get_collector()
        self.revisions = (
            self.run.revisions
                    .modified()
                    .filter(resource_type=self.content_type)
                    .order_by('created_at')
        )

    def apply(self, batch_size=500):
        """Apply the MODIFIED action in bulk.
        """
        paginator = Paginator(self.revisions, batch_size)

        for page_num in paginator.page_range:
            page = paginator.get_page(page_num)

            for revision in page.object_list:
                resource = self.collector.find_by_pk(revision.resource_id)
                metadata = revision.metadata.copy()
                set_attr = self.get_modify_function(metadata['field'])
                if resource:
                    set_attr(resource, revision=revision, **metadata)
                    self.collector.mark_as_processed(resource.pk)

            for resource in self.collector.processed:
                resource.save()

    def get_collector(self):
        """Get the object collector.
        """
        return ObjectCollector(self.get_queryset())

    def get_modify_function(self, field):
        """Check if this field has a special handler function, otherwise
        use the default modify function.
        """
        try:
            return getattr(self, 'modify_%s' % field)
        except AttributeError:
            return self.default_modify_function

    def default_modify_function(self, resource, field, new_value, *args, **kwargs):
        """Set the attribute for the provided resource.
        """
        setattr(resource, field, new_value)


class SchemaModifyAction(GenericModifyAction):
    """docstring for SchemaModifyAction
    """
    model_class = Schema

    def get_queryset(self):
        """Get the schemas related to this datastore.
        """
        return self.model_class.objects.filter(datastore_id=self.datastore.id)


class TableModifyAction(GenericModifyAction):
    """docstring for SchemaModifyAction
    """
    model_class = Table

    def get_queryset(self):
        """Get the schemas related to this datastore.
        """
        return self.model_class.objects.filter(schema__datastore_id=self.datastore.id)

    def modify_schema_id(self, table, field, new_value, revision, *args, **kwargs):
        """If the schema has been renamed, we need to update it manually.
        """
        if not new_value:
            schema = Schema.objects.get(
                created_revision_id=revision.parent_resource_revision_id
            )
            new_value = schema.pk

        if new_value != revision.metadata['new_value']:
            revision.metadata['new_value'] = new_value
            revision.save()

        table.schema_id = new_value


class ColumnModifyAction(GenericModifyAction):
    """docstring for ColumnModifyAction
    """
    model_class = Column

    def get_queryset(self):
        """Get the schemas related to this datastore.
        """
        return self.model_class.objects.filter(table__schema__datastore_id=self.datastore.id)


class IndexModifyAction(GenericModifyAction):
    """docstring for IndexModifyAction
    """
    model_class = Index

    def get_queryset(self):
        """Get the schemas related to this datastore.
        """
        return self.model_class.objects.filter(table__schema__datastore_id=self.datastore.id)

    def modify_columns(self, index, field, new_value, *args, **kwargs):
        """If columns have been updated, we need to reflect that change.
        """
        collector = ObjectCollector(
            collection=Column.objects.filter(table_id=index.table_id),
        )

        index_columns = []
        for column_metadata in new_value:
            column = collector.find_by_name(column_metadata['column_name'])
            index_column = {
                'column_id': column.pk,
                'index_id': index.pk,
                'workspace_id': index.workspace_id,
                'ordinal_position': column_metadata['ordinal_position'],
            }
            index_columns.append(index_column)

        results = IndexColumn.objects\
                             .on_conflict(['workspace_id', 'index_id', 'column_id'], ConflictAction.UPDATE)\
                             .bulk_insert(index_columns, only_fields=['ordinal_position'])

        index.index_columns.exclude(pk__in=[i['id'] for i in results]).delete()


def get_actions(*args, **kwargs):
    """Retrieve the modify action class based on the model name.
    """
    actions = {
        'Schema': SchemaModifyAction,
        'Table': TableModifyAction,
        'Column': ColumnModifyAction,
        'Index': IndexModifyAction,
    }
    return actions.items()
