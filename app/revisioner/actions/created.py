# -*- coding: utf-8 -*-
from django.core.paginator import Paginator

from app.definitions.models import Datastore, Schema, Table, Index, Column

from app.revisioner.models import Revision
from app.revisioner.collectors import ObjectCollector
from app.revisioner.revisioners import get_content_type_for_model

from utils.postgres.paginators import RawQuerySetPaginator
from utils.postgres.types import ConflictAction

from psycopg2.extensions import AsIs


class GenericCreateAction(object):
    """Generic mixin for a bulk CREATED action based on revisions.
    """
    conflict_target = None

    sql = '''
       SELECT DISTINCT COALESCE(r.parent_resource_id::varchar, p.resource_id::varchar, o.id::varchar) AS parent_instance_id, r.*
         FROM revisioner_revision r
    LEFT JOIN revisioner_revision p
           ON r.parent_resource_revision_id = p.revision_id
    LEFT JOIN %(db_table)s o
           ON r.parent_resource_revision_id = o.created_revision_id
        WHERE r.run_id = %(run)s
          AND r.resource_type_id = %(type)s
          AND r.action = 1
          AND r.applied_on IS NULL
     ORDER BY r.created_at
    '''

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
        )

    def get_paginator_class(self):
        return RawQuerySetPaginator

    def get_revisions(self):
        return Revision.objects.raw(self.sql, {'run': self.run.pk, 'type': self.content_type.pk, 'db_table': AsIs(self.parent_model_class._meta.db_table)})

    def bulk_insert(self, rows):
        """Perform a bulk INSERT and ignore duplicate records.
        """
        self.model_class.objects.on_conflict(self.conflict_target, ConflictAction.NOTHING).bulk_insert(rows)

    def apply(self, batch_size=2000):
        """Apply the CREATE action in bulk.
        """
        revisions = self.get_revisions()
        paginator = self.get_paginator_class()(revisions, batch_size)

        for page_num in paginator.page_range:
            page = paginator.get_page(page_num)

            self.logger.info(
                '[{0}] Started {1} of {2}'.format(self.model_class.__name__, page.end_index(), paginator.count)
            )

            data = [
                self.get_attributes(revision) for revision in page.object_list
            ]

            self.logger.info(
                '[{0}] Initialized {1} of {2}'.format(self.model_class.__name__, page.end_index(), paginator.count)
            )

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

    def get_paginator_class(self):
        return Paginator

    def get_revisions(self):
        return self.revisions.order_by('created_at')

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

    parent_model_class = Schema

    conflict_target = ['schema_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        schema_id = revision.parent_instance_id
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

    parent_model_class = Table

    conflict_target = ['table_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        table_id = revision.parent_instance_id
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

    parent_model_class = Table

    conflict_target = ['table_id', 'name']

    def get_attributes(self, revision):
        """Get the instance attributes from the Revision.
        """
        metadata = revision.metadata.copy()
        table_id = revision.parent_instance_id
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
        for revision in self.get_revisions():
            attributes, columns = self.get_attributes(revision)
            instance = self.model_class(**attributes)
            resources.append(instance)
            column_cache[instance.name] = columns

        instances = self.model_class.objects.bulk_create(resources, batch_size=500)
        collector = ObjectCollector(
            Column.objects.filter(table__schema__datastore_id=self.datastore.id)
        )

        for instance in instances:
            for c in column_cache.get(instance.name, []):
                column = collector.find_by(name__iexact=c['column_name'].lower(), table_id=instance.table_id)
                # column = collector.find_by(lambda t: (
                #     t.name.lower() == c['column_name'].lower() and t.table_id == instance.table_id
                # ))
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
