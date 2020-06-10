"""
Drop a table (`app`.`orderdetails`) and re-create it with the same name.

Example SQL:
  ALTER TABLE `app`.`orderdetails` RENAME `app`.`order_details`;

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16501
        ),
        "metadata": {
            "field": "table_name",
            "new_value": "order_details",
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16501
        ),
        "column_filters": (
            lambda col: col['column_name'] == "priceeach"
        ),
        "metadata": {
            "field": "columns.is_nullable",
            "new_value": True,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16501
        ),
        "column_filters": (
            lambda col: col['column_name'] == "priceeach"
        ),
        "metadata": {
            "field": "columns.numeric_scale",
            "new_value": 4,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16501
        ),
        "column_filters": (
            lambda col: col['column_name'] == "priceeach"
        ),
        "metadata": {
            "field": "columns.column_name",
            "new_value": "price_each",
        },
    },
])

inspected_indexes = mutate_inspected(inspected.indexes, [])

test_cases = [
    {
        "model": "Table",
        "description": "The `app`.`orderdetails` table should be modified.",
        "filters": {
            "object_id": "16501",
        },
        "assertions": [
            {
                "summarized": "It should rename `orderdetails` to `order_details`",
                "evaluation": lambda datastore, table: table.name,
                "pass_value": "order_details",
            },
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": "Hh2eS38kpRX0",
            },
            {
                "summarized": "It should not modify metadata about the Table.",
                "evaluation": lambda datastore, table: table.short_desc,
                "pass_value": "Details about an order",
            }
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`orderdetails`.`priceeach` column should be modified.",
        "filters": {
            "table__object_id": "16501",
            "name": "price_each",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identity.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "Hh2eS38kpRX0",
            },
            {
                "summarized": "It should retain the `object_id` value.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "16501/4",
            },
            {
                "summarized": "It should update `is_nullable` value.",
                "evaluation": lambda datastore, column: column.is_nullable,
                "pass_value": True,
            },
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": "ljbL6sdaSWLN",
            },
            {
                "summarized": "It should have modified the `numeric_scale` value.",
                "evaluation": lambda datastore, column: column.numeric_scale,
                "pass_value": 4,
            },
        ]
    },
]
