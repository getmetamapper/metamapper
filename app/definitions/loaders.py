# -*- coding: utf-8 -*-
from collections import defaultdict
from promise import Promise
from promise.dataloader import DataLoader

from app.definitions.models import Schema, Table, Column


class SchemaTableLoader(DataLoader):
    """Preload a collection of Table objects.
    """
    def batch_load_fn(self, schema_ids):
        """Function to process the batch load.
        """
        schema = Schema.objects.filter(object_id=schema_ids[0]).only('datastore_id').first()

        mapping = {s: [] for s in schema_ids}
        results = Table.objects.filter(schema__datastore_id=schema.datastore_id).order_by('name')

        for table in results:
            if table.schema_id not in schema_ids:
                continue
            mapping[table.schema_id].append(table)

        return Promise.resolve([
            mapping.get(s, []) for s in schema_ids
        ])


class TableColumnLoader(DataLoader):
    """Preload a collection of Column objects related to an Table.
    """
    def batch_load_fn(self, table_ids):
        """Function to process the batch load.
        """
        mapping = {t: [] for t in table_ids}
        results = Column.objects.filter(table_id__in=table_ids)
        is_processed = set()

        for column in results:
            if column.pk in is_processed:
                continue
            mapping[column.table_id].append(column)
            is_processed.add(column.pk)

        return Promise.resolve([
            mapping.get(s, []) for s in table_ids
        ])


class TableSchemaLoader(DataLoader):
    """Preload schemas related to a group of tables.
    """
    def batch_load_fn(self, schema_ids):
        """Function to process the batch load.
        """
        output = defaultdict(list)
        result = Schema.all_objects.filter(object_id__in=schema_ids)

        for schema_id in schema_ids:
            schema = next(filter(lambda q: q.object_id == schema_id, result), None)

            if schema and schema.is_deleted:
                schema.revive()

            output[schema_id] = schema

        return Promise.resolve([output.get(o) for o in schema_ids])
