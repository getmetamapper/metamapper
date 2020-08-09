# -*- coding: utf-8 -*-
from app.inspector import service as inspector
from app.revisioner.collectors import DefinitionCollector


def make(collector, *args, **kwargs):
    """We take an initial pass at making the definition based on the OID, if supported. The collector
    marks the raw database object as "processed" if we are able to match it to a Django model instance.
    """
    definition = {}

    list_of_indexes = inspector.indexes(collector.datastore)

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

        get_indexes = list(filter(lambda i: i['table_object_id'] == row['table_object_id'], list_of_indexes))

        for i in get_indexes:
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
            schema['instance'] = collector.schemas.search_unassigned(lambda t: (
                t.name == schema['name']
            ))

            if schema['instance']:
                collector.schemas.mark_as_processed(schema['instance'].pk)

        for table in definition[schema_name]['tables']:
            if not table['instance'] and schema['instance']:
                table['instance'] = collector.tables.search_unassigned(lambda t: (
                    t.name == table['name'] and t.schema_id == schema['instance'].pk
                ))

            if not table['instance']:
                continue

            collector.tables.mark_as_processed(table['instance'].pk)

            for column in table['columns']:
                if column['instance']:
                    continue

                column['instance'] = collector.columns.search_unassigned(lambda t: (
                    t.name == column['name'] and t.table_id == table['instance'].pk
                ))

                if column['instance']:
                    collector.columns.mark_as_processed(column['instance'].pk)

            for index in table['indexes']:
                if index['instance']:
                    continue

                index['instance'] = collector.indexes.search_unassigned(lambda t: (
                    t.name == index['name'] and t.table_id == table['instance'].pk
                ))

                if index['instance']:
                    collector.indexes.mark_as_processed(index['instance'].pk)

        if number > 0 and last_schema_name != schema_name:
            yield (last_schema_name, definition.pop(last_schema_name))

        last_schema_name = schema_name

    for schema_name in definition.keys():
        yield (schema_name, definition[schema_name])


def hydrate(datastore, definition, *args, **kwargs):
    """Populate a definition pulled from blob storage with data.
    """
    collector = DefinitionCollector(datastore)

    schema_instance = definition['schema'].get('instance')
    if schema_instance:
        schemas = collector.mapper[schema_instance['type']]
        definition['schema']['instance'] = schemas.find_by_pk(schema_instance['pk'])

    for table in definition['tables']:
        table_instance = table.get('instance')
        if table_instance:
            tables = collector.mapper[table_instance['type']]
            table['instance'] = tables.find_by_pk(table_instance['pk'])

        for column in table['columns']:
            column_instance = column.get('instance')
            if column_instance:
                columns = collector.mapper[column_instance['type']]
                column['instance'] = columns.find_by_pk(column_instance['pk'])

        for index in table['indexes']:
            index_instance = index.get('instance')
            if index_instance:
                indexes = collector.mapper[index_instance['type']]
                index['instance'] = indexes.find_by_pk(index_instance['pk'])
    return definition
