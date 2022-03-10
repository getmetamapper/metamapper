"""
Existing table (`app`.`customers`) is moved to
the `employees` schema.

Example SQL:

  ALTER TABLE `app`.`customers`
       RENAME `employees`.`customers`;

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16442
        ),
        "metadata": {
            "field": "table_schema",
            "new_value": "employees",
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16442
        ),
        "metadata": {
            "field": "schema_object_id",
            "new_value": 16386,
        },
    },
])

test_cases = [
    {
        "model": "Table",
        "description": "The `app`.`customers` table should move to the `employees` schema.",
        "filters": {
            "object_id": "16442",
        },
        "assertions": [
            {
                "summarized": "It should retain the same primary key.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 1,
            },
            {
                "summarized": "It should reference the `employees` Schema instance by ID.",
                "evaluation": lambda datastore, table: table.schema_id,
                "pass_value": 2,
            },
            {
                "summarized": "It should reference the `employees` Schema instance by name.",
                "evaluation": lambda datastore, table: table.schema.name,
                "pass_value": "employees",
            },
        ]
    },
]
