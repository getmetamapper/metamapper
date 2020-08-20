# -*- coding: utf-8 -*-
from app.definitions.models import Schema, Table, Column, Index, IndexColumn

from app.revisioner.models import Revision
from app.revisioner.collectors import ObjectCollector
from app.revisioner.revisioners import get_content_type_for_model

from utils.postgres.paginators import RawQuerySetPaginator
from utils.postgres.types import ConflictAction
from utils.shortcuts import model_to_dict


class GenericModifyAction(object):
    """Generic mixin for a bulk CREATED action based on revisions.
    """
    sql = '''
    WITH revisioner_changes AS (
          SELECT resource_id, ARRAY_AGG(metadata) AS "changes"
            FROM revisioner_revision
           WHERE run_id = %(run)s
             AND resource_type_id = %(type)s
             AND action = 2
        GROUP BY resource_id
    )

    SELECT r.*, c.changes
      FROM revisioner_revision r
      JOIN revisioner_changes c
        ON r.resource_id = c.resource_id
     WHERE r.run_id = %(run)s
       AND r.resource_type_id = %(type)s
       AND r.action = 2
       AND r.applied_on IS NULL
     ORDER BY r.created_at
    '''

    def __init__(self, run, datastore, logger, *args, **kwargs):
        self.run = run
        self.datastore = datastore
        self.logger = logger
        self.content_type = get_content_type_for_model(self.model_class)
        self.collector = self.get_collector()
        self.revisions = (
            self.run.revisions
                    .modified()
                    .filter(resource_type=self.content_type)
        )

    def bulk_update(self, rows):
        """Perform a bulk UPSERT based on the provided ident.
        """
        self.model_class.objects.on_conflict(['id'], ConflictAction.UPDATE).bulk_insert(rows)

    def get_paginator_class(self):
        return RawQuerySetPaginator

    def get_revisions(self):
        return Revision.objects.raw(self.sql, {'run': self.run.pk, 'type': self.content_type.pk})

    def apply(self, batch_size=250):
        """Apply the MODIFIED action in bulk.
        """
        revisions = self.get_revisions()
        paginator = self.get_paginator_class()(revisions, batch_size)
        processed = set()

        for page_num in paginator.page_range:
            page = paginator.get_page(page_num)
            data = []

            for revision in page.object_list:
                if revision.resource_id in processed:
                    continue
                resource = self.collector.find_by_pk(revision.resource_id)
                if not resource:
                    continue
                for metadata in revision.changes:
                    set_attr = self.get_modify_function(metadata['field'])
                    set_attr(resource, revision=revision, **metadata)
                data.append(model_to_dict(resource, exclude=['columns']))
                processed.add(revision.resource_id)

            if len(data):
                self.bulk_update(data)

            self.logger.info(
                '[{0}] Modified {1} of {2}'.format(self.model_class.__name__, page.end_index(), paginator.count)
            )

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
        collector = ObjectCollector(Column.objects.filter(table_id=index.table_id))

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
