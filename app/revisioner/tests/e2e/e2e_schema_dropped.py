"""
Drop an entire schema (`app`).

Example SQL:

  DROP SCHEMA `app`;

We would expect the schema and it's children to be removed.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['schema_object_id'] == 16441
        ),
    },
])

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16441
        ),
    },
])

test_cases = [
    {
        "model": "Schema",
        "description": "The `app` schema should not longer exist.",
        "filters": {
            "name": "16441",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `object_id` value.",
                "evaluation": lambda datastore, schema: schema is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Schema",
        "description": "The `app` schema should not longer exist.",
        "filters": {
            "name": "app",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `name` value.",
                "evaluation": lambda datastore, schema: schema is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Schema",
        "description": "The `app` schema should not longer exist.",
        "filters": {
            "pk": 1,
        },
        "assertions": [
            {
                "summarized": "It should not be found via `pk` value.",
                "evaluation": lambda datastore, schema: schema is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `app` schema should have no tables.",
        "filters": {
            "schema_id": 1,
        },
        "assertions": [
            {
                "summarized": "It should not be found via `schema_id` value.",
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `app` schema should have no tables.",
        "filters": {
            "schema__name": "app",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `schema__name` value.",
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `app` schema should have no indexes.",
        "filters": {
            "table__schema_id": 1,
        },
        "assertions": [
            {
                "summarized": "It should not be found via `schema_id` value.",
                "evaluation": lambda datastore, index: index is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `app` schema should have no indexes.",
        "filters": {
            "table__schema__name": "app",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `schema__name` value.",
                "evaluation": lambda datastore, index: index is None,
                "pass_value": True,
            },
        ]
    },
]
