"""
Drop a table (`app`.`orderdetails`) and re-create it with the same name.

Example SQL:
  ALTER TABLE `app`.`orderdetails` RENAME `app`.`order_details`;

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ["datastore", "relationships"]

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

test_cases = [
    {
        "model": "Table",
        "description": "The `app`.`orderdetails` table should be modified.",
        "filters": {
            "object_ref": "16501",
        },
        "assertions": [
            {
                "summarized": "It should rename `orderdetails` to `order_details`.",
                "evaluation": lambda datastore, table: table.name,
                "pass_value": "order_details",
            },
            {
                "summarized": "It should not modify metadata about the Table.",
                "evaluation": lambda datastore, table: table.short_desc,
                "pass_value": "Details about an order",
            },
            {
                "summarized": "It should update the Table object ID.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "d3b1a0e8bebc6de5627c7ab7d4361d2e",
            },
            # TODO(scruwys): This fails.
            {
                "summarized": "It should not update the Table primary key.",
                "evaluation": lambda datastore, table: table.id,
                "pass_value": 3,
            },
            {
                "summarized": "It should not modify notes about the Table.",
                "evaluation": lambda datastore, table: table.comments.count() > 0,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`orderdetails` table should have the same columns.",
        "filters": {
            "table_id": "d3b1a0e8bebc6de5627c7ab7d4361d2e",
        },
        "assertions": [
            {
                "summarized": "It should update the foreign relationship.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "d3b1a0e8bebc6de5627c7ab7d4361d2e",
            },
            {
                "summarized": "It should retain the same column name.",
                "evaluation": lambda datastore, column: column.name,
                "pass_value": "ordernumber",
            },
            {
                "summarized": "It should retain the Column metadata.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": "The primary key of the table.",
            },
            {
                "summarized": "It should update the Column object ID.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "2f2ea275fecb310ab4a47ba25b9ecc78",
            },
            {
                "summarized": "It should not update the primary key of the Column.",
                "evaluation": lambda datastore, column: column.id,
                "pass_value": 16,
            },
            {
                "summarized": "It should retain the related notes.",
                "evaluation": lambda datastore, column: column.comments.count() > 0,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`orderdetails`.`priceeach` column should be modified.",
        "filters": {
            "table__object_ref": "16501",
            "name": "price_each"
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identity.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "d3b1a0e8bebc6de5627c7ab7d4361d2e",
            },
            {
                "summarized": "It should retain the `object_id` value.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "78930268e8c817373da24d5bc90a7b32",
            },
            {
                "summarized": "It should update `is_nullable` value.",
                "evaluation": lambda datastore, column: column.is_nullable,
                "pass_value": True,
            },
            {
                "summarized": "It should have the same Column metadata.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": "The price of each item.",
            },
            {
                "summarized": "It should have modified the `numeric_scale` value.",
                "evaluation": lambda datastore, column: column.numeric_scale,
                "pass_value": 4,
            },
        ]
    },
]
