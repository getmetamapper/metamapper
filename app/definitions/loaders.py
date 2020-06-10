# -*- coding: utf-8 -*-
from promise import Promise
from promise.dataloader import DataLoader
from django.db.models import F

from app.definitions.models import Schema, Table, Column


class SchemaTableLoader(DataLoader):
    """Preload a collection of Table objects.
    """
    def batch_load_fn(self, schema_ids):
        """Function to process the batch load.
        """
        schemas = Schema.objects.filter(id__in=schema_ids).order_by('name')
        mapping = {s.pk: [] for s in schemas}
        results = Table.objects.filter(schema_id__in=schema_ids).order_by('name')

        for table in results:
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


class IndexColumnLoader(DataLoader):
    """Preload a collection of Column objects related to an Index.
    """
    def batch_load_fn(self, index_ids):
        """Function to process the batch load.
        """
        mapping = {i: [] for i in index_ids}
        results = Column.objects\
                        .filter(indexcolumn__index_id__in=index_ids)\
                        .annotate(index_id=F('indexcolumn__index_id'))\
                        .order_by('indexcolumn__ordinal_position')

        for column in results:
            mapping[column.index_id].append(column)

        return Promise.resolve([
            list(set(mapping.get(s, []))) for s in index_ids
        ])
