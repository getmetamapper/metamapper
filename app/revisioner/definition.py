# -*- coding: utf-8 -*-
from collections import defaultdict

from app.inspector import service as inspector


class DefinitionProcessor(object):
    """docstring for Processor
    """
    def __init__(self, collector, logger=None):
        self.collector = collector
        self.datastore = self.collector.datastore
        self._indexes = None
        self.logger = logger

    @property
    def indexes(self):
        if self._indexes is None:
            index_dict = defaultdict(list)
            for index in inspector.indexes(self.datastore):
                index_dict[index['table_object_id']].append(index)
            self._indexes = index_dict
        return self._indexes

    def map(self, f, items):
        """Apply a function to a set of items.
        """
        return list(map(f, items))

    def execute(self):
        """Process and create the definition for the datastore.
        """
        definition = {}

        last_schema_name = None

        for number, row in enumerate(inspector.tables_and_views(self.datastore)):
            schema_name = row.pop('table_schema')

            if schema_name not in definition:
                definition[schema_name] = {
                    'schema': {
                        'instance': self.collector.schemas.find_by_oid(row['schema_object_id']),
                        'name': schema_name,
                        'object_id': row['schema_object_id'],
                    },
                    'tables': [],
                }

            columns = self.map(self.process_column, row['columns'])
            indexes = self.map(self.process_index, self.indexes[row['table_object_id']])

            definition[schema_name]['tables'].append({
                'instance': self.collector.tables.find_by_oid(row['table_object_id']),
                'name': row['table_name'],
                'kind': row['table_type'],
                'object_id': row['table_object_id'],
                'columns': columns,
                'indexes': indexes,
            })

            if number > 0 and last_schema_name != schema_name:
                schema = definition[last_schema_name]['schema']

                if not schema['instance']:
                    schema['instance'] = self.collector.schemas.search_unassigned(name=schema['name'])

                for table in definition[last_schema_name]['tables']:
                    if not table['instance'] and schema['instance']:
                        table['instance'] = self.collector.tables.search_unassigned(
                            name=table['name'],
                            schema_id=schema['instance'].pk,
                        )

                    if not table['instance']:
                        continue

                    for column in table['columns']:
                        if column['instance']:
                            continue

                        column['instance'] = self.collector.columns.search_unassigned(
                            name=column['name'],
                            table_id=table['instance'].pk,
                        )

                    for index in table['indexes']:
                        if index['instance']:
                            continue

                        index['instance'] = self.collector.indexes.search_unassigned(
                            name=index['name'],
                            table_id=table['instance'].pk,
                        )

                yield (last_schema_name, definition.pop(last_schema_name))

            last_schema_name = schema_name

        for schema_name in definition.keys():
            yield (schema_name, definition[schema_name])

    def process_column(self, column, *args, **kwargs):
        """Format columns for processing.
        """
        column_instance = self.collector.columns.find_by_oid(column['column_object_id'])
        column['instance'] = column_instance
        column['name'] = column.pop('column_name')
        column['object_id'] = column.pop('column_object_id')
        column['db_comment'] = column.pop('column_description')
        return column

    def process_index(self, index, *args, **kwargs):
        """Format indices for processing.
        """
        index_instance = self.collector.indexes.find_by_oid(index['index_object_id'])
        index_kwargs = {
            'name': index['index_name'],
            'instance': index_instance,
            'object_id': index['index_object_id'],
            'is_primary': index.get('is_primary', False),
            'is_unique': index.get('is_unique', False),
            'sql': index.get('definition'),
            'columns': index['columns'],
        }
        return index_kwargs
