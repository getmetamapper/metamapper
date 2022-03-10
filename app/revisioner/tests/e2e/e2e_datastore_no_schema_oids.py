"""
This tests when a Datastore renames a schema, but the object ID does not persist.

We would expect the children objects to persist since OIDs persist, but the schema
object would be destroyed.

This is expected functionality within MySQL databases.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "modified",
        "filters": (
            lambda row: row['schema_object_id'] == 16441
        ),
        "metadata": {
            "field": "table_schema",
            "new_value": "tng",
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['schema_object_id'] == 16441
        ),
        "metadata": {
            "field": "schema_object_id",
            "new_value": 99999,
        },
    },
])

test_cases = [
    {
        "model": "Schema",
        "description": "The `app` schema has been dropped.",
        "filters": {
            "name": "app",
        },
        "assertions": [
            {
                "summarized": "The `app` schema does not exist.",
                "evaluation": lambda datastore, schema: schema is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Schema",
        "description": "The renamed `tng` schema should have the same identity.",
        "filters": {
            "name": "tng",
        },
        "assertions": [
            {
                "summarized": "The `tng` schema has different identity as the `app` schema.",
                "evaluation": lambda datastore, schema: schema.pk == "tThdqoa6Huxs",
                "pass_value": False,
            },
            {
                "summarized": "The `tng` schema has the same tables as the `app` schema",
                "evaluation": lambda datastore, schema: set(schema.tables.values_list("name", flat=True)),
                "pass_value": {
                    "customers",
                    "departments",
                    "payments",
                    "orders",
                    "orderdetails",
                    "products",
                    "productlines",
                    "sales_representatives",
                },
            },
        ]
    },
    {
        "model": "Table",
        "description": "Tests related to the `tng` tables.",
        "filters": {
            "object_ref": "16442",
        },
        "assertions": [
            {
                "summarized": "The table should have the same name.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 1,
            },
        ]
    },
    {
        "model": "Table",
        "description": "Tests related to the `tng` tables.",
        "filters": {
            "object_ref": "16465",
        },
        "assertions": [
            {
                "summarized": "The table should have the same name.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 4,
            },
        ]
    },
    {
        "model": "Table",
        "description": "Tests related to the `tng` tables.",
        "filters": {
            "object_ref": "16392",
        },
        "assertions": [
            {
                "summarized": "The table should have the same name.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 10,
            },
        ]
    },
]
