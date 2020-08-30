# -*- coding: utf-8 -*-
from app.inspector import service as inspector


def make(collector, *args, **kwargs):  # noqa: C901
    """We take an initial pass at making the definition based on the OID, if supported. The collector
    marks the raw database object as "processed" if we are able to match it to a Django model instance.
    """
    index_list = inspector.indexes(collector.datastore)
    definition = {}

    last_schema_name = None

    for number, row in enumerate(inspector.tables_and_views(collector.datastore)):
        schema_name = row.pop('table_schema')

        if schema_name not in definition:
            schema_instance = collector.schemas.find_by_oid(row['schema_object_id'])

            if schema_instance:
                collector.schemas.mark_as_processed(schema_instance.pk)

            definition[schema_name] = {
                'schema': {
                    'instance': schema_instance,
                    'name': schema_name,
                    'object_id': row['schema_object_id'],
                },
                'tables': [],
            }

        columns = []
        indexes = []

        table_instance = collector.tables.find_by_oid(row['table_object_id'])
        if table_instance:
            collector.tables.mark_as_processed(table_instance.pk)

        for c in row['columns']:
            column = c.copy()
            column_instance = collector.columns.find_by_oid(column['column_object_id'])
            if column_instance:
                collector.columns.mark_as_processed(column_instance.pk)
            column['name'] = column.pop('column_name')
            column['instance'] = column_instance
            column['object_id'] = column.pop('column_object_id')
            columns.append(column)

        for i in filter(lambda i: i['table_object_id'] == row['table_object_id'], index_list):
            index = i.copy()
            index_instance = collector.indexes.find_by_oid(index['index_object_id'])

            if index_instance:
                collector.indexes.mark_as_processed(index_instance.pk)

            indexes.append({
                'name': index['index_name'],
                'instance': index_instance,
                'object_id': index['index_object_id'],
                'is_primary': index.get('is_primary', False),
                'is_unique': index.get('is_unique', False),
                'sql': index.get('definition'),
                'columns': index['columns'],
            })

        # We append the final TABLE or VIEW object to the relevant schema.
        definition[schema_name]['tables'].append({
            'instance': table_instance,
            'name': row['table_name'],
            'kind': row['table_type'],
            'object_id': row['table_object_id'],
            'columns': columns,
            'indexes': indexes,
        })

        schema = definition[schema_name]['schema']

        if not schema['instance']:
            schema['instance'] = collector.schemas.search_unassigned(name=schema['name'])

            if schema['instance']:
                collector.schemas.mark_as_processed(schema['instance'].pk)

        for table in definition[schema_name]['tables']:
            if not table['instance'] and schema['instance']:
                table['instance'] = collector.tables.search_unassigned(name=table['name'], schema_id=schema['instance'].pk)

            if not table['instance']:
                continue

            collector.tables.mark_as_processed(table['instance'].pk)

            for column in table['columns']:
                if column['instance']:
                    continue

                column['instance'] = collector.columns.search_unassigned(name=column['name'], table_id=table['instance'].pk)

                if column['instance']:
                    collector.columns.mark_as_processed(column['instance'].pk)

            for index in table['indexes']:
                if index['instance']:
                    continue

                index['instance'] = collector.indexes.search_unassigned(name=index['name'], table_id=table['instance'].pk)

                if index['instance']:
                    collector.indexes.mark_as_processed(index['instance'].pk)

        if number > 0 and last_schema_name != schema_name:
            yield (last_schema_name, definition.pop(last_schema_name))

        last_schema_name = schema_name

    for schema_name in definition.keys():
        yield (schema_name, definition[schema_name])
