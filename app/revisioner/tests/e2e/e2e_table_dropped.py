"""
Drop a table (`employees`.`departments`).

Example SQL:

  DROP TABLE `employees`.`departments`;

We would expect the table and it's children to be removed.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16392
        ),
    },
])

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16392
        ),
    },
])

test_cases = [
    {
        "model": "Table",
        "description": "The `employees`.`departments` table should not longer exist.",
        "filters": {
            "object_id": "16392",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `object_id` value.",
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `employees`.`departments` table should not longer exist.",
        "filters": {
            "pk": "IFMwWB5gtslY",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `pk` value.",
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `employees`.`departments` table should not longer exist.",
        "filters": {
            "schema__name": "employees",
            "name": "departments",
        },
        "assertions": [
            {
                "summarized": "It should not be found via `name` value.",
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `employees`.`departments` table should have no columns.",
        "filters": {
            "table_id": "IFMwWB5gtslY",
        },
        "assertions": [
            {
                "summarized": "It should not find any columns associated with this identity.",
                "evaluation": lambda datastore, column: column is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `employees`.`departments` table should have no indexes.",
        "filters": {
            "table_id": "IFMwWB5gtslY",
        },
        "assertions": [
            {
                "summarized": "It should not find any indexes associated with this identity.",
                "evaluation": lambda datastore, index: index is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `app`.`departments` table should still exist.",
        "filters": {
            "schema__name": "app",
            "name": "departments",
        },
        "assertions": [
            {
                "summarized": "It should have the expected `pk` value.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": "got35fs8LymV",
            },
            {
                "summarized": "It should have the expected `object_id` value.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "16522",
            },
            {
                "summarized": "It should still have a table structure.",
                "evaluation": lambda datastore, table: table.columns.count(),
                "pass_value": 2,
            },
        ]
    },
]
