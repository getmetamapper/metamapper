# -*- coding: utf-8 -*-
from hashlib import md5
from app.inspector import service as inspector


class SchemaDefinitionCollector(object):
    """Class that prepares the inspected schema definition for ingestion.
    """
    def __init__(self, datastore):
        self.datastore = datastore

    def map(self, f, items):
        """Apply a function to a set of items.
        """
        return list(map(f, items))

    def hash(self, *args):
        """Create MD5 hash of the provided arguments.
        """
        return md5(''.join(map(str, args)).encode()).hexdigest()

    def verify_connection(self):
        """Verify datastore can be connected to.
        """
        return inspector.verify_connection(self.datastore)

    def execute(self, run):
        """Process and create the definition for the datastore.
        """
        definition = {}

        last_schema_name = None

        for number, row in enumerate(inspector.tables_and_views(self.datastore)):
            schema_name = row.pop('table_schema')
            schema_object_id = self.hash(self.datastore.id, schema_name)

            if schema_name not in definition:
                definition[schema_name] = {
                    'schema': {
                        'run_id': run.id,
                        'datastore_id': self.datastore.id,
                        'workspace_id': self.datastore.workspace_id,
                        'name': schema_name,
                        'object_ref': row['schema_object_id'],
                        'object_id': schema_object_id,
                        'deleted_at': None,
                    },
                    'tables': [],
                }

            table_object_id = self.hash(schema_object_id, row['table_name'])

            columns = []
            for column in row['columns']:
                columns.append(
                    self.process_column(column, run.id, table_object_id))

            definition[schema_name]['tables'].append({
                'run_id': run.id,
                'schema_id': schema_object_id,
                'workspace_id': self.datastore.workspace_id,
                'kind': row['table_type'],
                'name': row['table_name'],
                'object_id': table_object_id,
                'object_ref': row['table_object_id'],
                'columns': columns,
                'deleted_at': None,
            })

            if number > 0 and last_schema_name != schema_name:
                yield (last_schema_name, definition.pop(last_schema_name))

            last_schema_name = schema_name

        for schema_name in definition.keys():
            yield (schema_name, definition[schema_name])

    def process_column(self, column, run_id, table_id):
        """Format columns for processing.
        """
        column['run_id'] = run_id
        column['table_id'] = table_id
        column['workspace_id'] = self.datastore.workspace_id
        column['name'] = column.pop('column_name')
        column['db_comment'] = column.pop('column_description')
        column['object_ref'] = column.pop('column_object_id')
        column['object_id'] = self.hash(table_id, column['name'])
        column['deleted_at'] = None
        return column
