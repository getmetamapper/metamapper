# -*- coding: utf-8 -*-
import json

import app.definitions.models as models
import app.inspector.service as inspector


def format_datastore(datastore):
    """Convert Datastore to fixture format.
    """
    return {
        "fields": {
            "name": datastore.name,
            "slug": datastore.slug,
            "workspace_id": str(datastore.workspace_id),
            "created_at": str(datastore.created_at),
            "updated_at": str(datastore.updated_at),
            "host": "database.host",
            "port": 5432,
            "username": "admin",
            "password": "password1234",
            "engine": datastore.engine,
            "version": "9.6.1"
        },
        "model": "definitions.datastore",
        "pk": datastore.pk,
    }


def format_schema(schema):
    """Convert Schema to fixture format.
    """
    return {
        "fields": {
            "name": schema.name,
            "datastore_id": schema.datastore_id,
            "workspace_id": str(schema.workspace_id),
            "created_at": str(schema.created_at),
            "updated_at": str(schema.updated_at),
            "object_id": schema.object_id,
            "tags": schema.tags,
        },
        "model": "definitions.schema",
        "pk": schema.pk,
    }


def format_table(table):
    """Convert Table to fixture format.
    """
    return {
        "fields": {
            "name": table.name,
            "schema_id": table.schema_id,
            "workspace_id": str(table.workspace_id),
            "created_at": str(table.created_at),
            "updated_at": str(table.updated_at),
            "object_id": table.object_id,
            "kind": table.kind,
            "tags": table.tags,
            "short_desc": table.short_desc,
            "properties": table.properties,
        },
        "model": "definitions.table",
        "pk": table.pk,
    }


def format_column(column):
    """Convert Column to fixture format.
    """
    return {
        "fields": {
            "name": column.name,
            "table_id": column.table_id,
            "workspace_id": str(column.workspace_id),
            "created_at": str(column.created_at),
            "updated_at": str(column.updated_at),
            "object_id": column.object_id,
            "is_nullable": column.is_nullable,
            "is_primary": column.is_primary,
            "ordinal_position": column.ordinal_position,
            "data_type": column.data_type,
            "numeric_scale": column.numeric_scale,
            "max_length": column.max_length,
            "default_value": column.default_value,
        },
        "model": "definitions.column",
        "pk": column.pk,
    }


def format_index(index):
    """Convert Index to fixture format.
    """
    return {
        "fields": {
            "name": index.name,
            "table_id": index.table_id,
            "workspace_id": str(index.workspace_id),
            "created_at": str(index.created_at),
            "updated_at": str(index.updated_at),
            "object_id": index.object_id,
            "is_unique": index.is_unique,
            "is_primary": index.is_primary,
            "sql": index.sql,
        },
        "model": "definitions.index",
        "pk": index.pk,
    }


def format_index_column(index_column):
    """Convert Index to fixture format.
    """
    return {
        "fields": {
            "index_id": index_column.index_id,
            "column_id": index_column.column_id,
            "workspace_id": str(index_column.workspace_id),
            "created_at": str(index_column.created_at),
            "updated_at": str(index_column.updated_at),
            "ordinal_position": index_column.ordinal_position,
        },
        "model": "definitions.indexcolumn",
        "pk": index_column.pk,
    }


def main(datastore_slug, schemas):
    """
    """
    datastore = models.Datastore.objects.get(slug__iexact=datastore_slug)
    responses = [format_datastore(datastore)]

    for schema in datastore.schemas.all():
        responses.append(format_schema(schema))

        for table in schema.tables.all():
            responses.append(format_table(table))

            for column in table.columns.all():
                responses.append(format_column(column))

            for index in table.indexes.all():
                responses.append(format_index(index))

                for index_column in index.index_columns.all():
                    responses.append(format_index_column(index_column))

    with open('dev/datastores/%s/extracts/fixtures.json' % datastore.engine, 'w') as outfile:
        outfile.write(json.dumps(responses, indent=2))

    # tables_and_views = inspector.tables_and_views(datastore)
    # indexes = inspector.indexes(datastore)
    tables_and_views = [
        i for i in inspector.tables_and_views(datastore)
        if i['table_schema'] in schemas.keys() and i['table_name'] in schemas[i['table_schema']]
    ]

    indexes = [
        i for i in inspector.indexes(datastore)
        if i['schema_name'] in schemas.keys() and i['table_name'] in schemas[i['schema_name']]
    ]

    with open('dev/datastores/%s/extracts/tables_and_views.json' % datastore.engine, 'w') as outfile:
        outfile.write(json.dumps(tables_and_views, indent=2))

    with open('dev/datastores/%s/extracts/indexes.json' % datastore.engine, 'w') as outfile:
        outfile.write(json.dumps(indexes, indent=2))


if __name__ == '__main__':
    from app.revisioner.tests.e2e import script
    schemas = {
        'public': [
            'users',
            'permissions',
            'groups',
        ]
    }
    script.main('postgres', schemas)

    schemas = {
        'classicmodels': [
            'orders',
            'orderdetails',
            'customers',
        ],
        'salika': [
            'actor',
            'film',
            'film_actor',
        ]
    }
    script.main('mysql-database', schemas)

    schemas = {
        'employees': [
            'employees',
            'departments',
            'dept_manager',
            'dept_emp',
        ]
    }
    script.main('snowflake', schemas)
