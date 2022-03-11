"""
Rename the `app` schema to `public` with a persistent `schema`.`object_id`.

Example SQL:

  ALTER SCHEMA `app` RENAME `public`;
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "modified",
        "filters": (
            lambda row: row["schema_object_id"] == 16441
        ),
        "metadata": {
            "field": "table_schema",
            "new_value": "public",
        },
    },
])

test_cases = [
    {
        "model": "Schema",
        "description": "Expect the `app` schema to be renamed to `public`.",
        "filters": {
            "name": "public",
            "object_ref": "16441",
        },
        "assertions": [
            {
                "summarized": "It should retain existing tables.",
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
            {
                "summarized": "It should retain existing attributes.",
                "evaluation": lambda datastore, schema: set(schema.tags),
                "pass_value": {
                    "one",
                    "two",
                    "three",
                }
            }
        ]
    },
]
