"""
This tests when a Datastore experiences some typical changes to the underlying definition.

Test Cases:

  - Table is renamed.
  - Table is created.
  - Table is dropped.
  - Column is dropped.
  - [PENDING] Column attributes are updated.

"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    # (1) We renamed the table `employee.departments` to `employee.depts`.
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16392
        ),
        "metadata": {
            "field": "table_name",
            "new_value": "depts",
        },
    },
    # (2) We dropped the `app`.`productlines` table at some point.
    {
        "type": "dropped",
        "description": "",
        "filters": (
            lambda row: row['table_object_id'] == 16456
        ),
    },
    # (3) We dropped the `app`.`productlines` table at some point.
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16488
        ),
        "column_filters": (
            lambda col: col['column_object_id'] == "16488/9"
        ),
    },
    # (4) The column `app`.`customers`.`postalcode` has a `default_value` change.
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16442
        ),
        "column_filters": (
            lambda col: col['column_name'] == "postalcode"
        ),
        "metadata": {
            "field": "columns.default_value",
            "new_value": "default_sequence()",
        },
    },
    # (5) The column `app`.`orders`.`status` has a data type change.
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16465
        ),
        "column_filters": (
            lambda col: col['column_name'] == "status"
        ),
        "metadata": {
            "field": "columns.data_type",
            "new_value": "integer",
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16465
        ),
        "column_filters": (
            lambda col: col['column_name'] == "status"
        ),
        "metadata": {
            "field": "columns.max_length",
            "new_value": 50,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16465
        ),
        "column_filters": (
            lambda col: col['column_name'] == "status"
        ),
        "metadata": {
            "field": "columns.numeric_scale",
            "new_value": 0,
        },
    },
    # (6) The column `app`.`orders`.`amount` is changed.
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16478
        ),
        "column_filters": (
            lambda col: col['column_name'] == "amount"
        ),
        "metadata": {
            "field": "columns.is_nullable",
            "new_value": True,
        },
    },
    {
        "type": "modified",
        "filters": (
            lambda row: row['table_object_id'] == 16478
        ),
        "column_filters": (
            lambda col: col['column_name'] == "amount"
        ),
        "metadata": {
            "field": "columns.column_name",
            "new_value": "dollar_amount",
        },
    },
])

# (7) We create a brand new table called `app.categories`.
inspected_tables += [
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 99999,
        "table_name": "categories",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "99999/1",
                "column_name": "category_id",
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "99999/1",
                "column_name": "name",
                "ordinal_position": 2,
                "data_type": "varchar",
                "max_length": 256,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
        ]
    }
]

inspected_indexes = mutate_inspected(inspected.indexes, [])

test_cases = [
    {
        "model": "Table",
        "description": "Expect `employees.departments` table to be renamed.",
        "filters": {
            "schema__name": "employees",
            "object_id": "16392",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table.name,
                "pass_value": "depts",
            }
        ]
    },
    {
        "model": "Table",
        "description": "Expect `app.departments` table NOT be be renamed.",
        "filters": {
            "schema__name": "app",
            "object_id": "16522",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table.name,
                "pass_value": "departments",
            }
        ]
    },
    {
        "model": "Table",
        "description": "Expect `app.productlines` table to be deleted.",
        "filters": {
            "schema__name": "app",
            "name": "productlines",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table,
                "pass_value": None,
            }
        ],
    },
    {
        "model": "Column",
        "description": "Expect `app.productlines` columns to be deleted.",
        "filters": {
            "table__schema__name": "app",
            "table__name": "productlines",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column,
                "pass_value": None,
            }
        ],
    },
    {
        "model": "Column",
        "description": "Expect `app.products.msrp` column to be deleted.",
        "filters": {
            "pk": 44,
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column,
                "pass_value": None,
            }
        ],
    },
    {
        "model": "Table",
        "description": "Expect `app.categories` table to be created.",
        "filters": {
            "schema__name": "app",
            "name": "categories",
            "object_id": "99999",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table.name,
                "pass_value": "categories",
            },
            {
                "evaluation": lambda datastore, table: table.columns.count(),
                "pass_value": 2,
            }
        ]
    },
    {
        "model": "Column",
        "description": "The column `app`.`customers`.`postalcode` has a default_value change.",
        "filters": {
            "table__schema__name": "app",
            "table__object_id": "16442",
            "name": "postalcode",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column.ordinal_position,
                "pass_value": 10,
            },
            {
                "evaluation": lambda datastore, column: column.default_value,
                "pass_value": "default_sequence()",
            }
        ]
    },
    {
        "model": "Column",
        "description": "The column `app`.`orders`.`status` has a data type change.",
        "filters": {
            "table__schema__name": "app",
            "table__object_id": "16465",
            "name": "status",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column.data_type,
                "pass_value": "integer",
            },
            {
                "evaluation": lambda datastore, column: column.max_length,
                "pass_value": 50,
            },
            {
                "evaluation": lambda datastore, column: column.numeric_scale,
                "pass_value": 0,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The column `app`.`orders`.`amount` has changed.",
        "filters": {
            "table__schema__name": "app",
            "table__object_id": "16478",
            "ordinal_position": 4,
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column.full_data_type,
                "pass_value": "numeric(10, 2)",
            },
            {
                "evaluation": lambda datastore, column: column.is_nullable,
                "pass_value": True,
            },
            {
                "evaluation": lambda datastore, column: column.name,
                "pass_value": "dollar_amount",
            },
        ]
    },
    {
        "model": "Index",
        "description": "Expect `customers_pkey` index to be created.",
        "filters": {
            "table__schema__name": "app",
            "name": "customers_pkey",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, index: index.object_id,
                "pass_value": "16449",
            },
            {
                "evaluation": lambda datastore, index: index.columns.count() > 0,
                "pass_value": True,
            }
        ]
    },
]
