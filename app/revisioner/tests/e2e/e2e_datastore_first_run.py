"""
Tests when a fresh Datastore is added. No other items exist in the workspace.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = []

inspected_tables = mutate_inspected(inspected.tables_and_views, [])

test_cases = [
    {
        "description": "Expect new schemas to be created.",
        "assertions": [
            {
                "evaluation": lambda datastore, nulled: set(datastore.schemas.values_list("name", flat=True)),
                "pass_value": {
                    "app",
                    "employees",
                },
            },
        ]
    },
    {
        "model": "Schema",
        "description": "Expect the `app` schema to be created.",
        "filters": {
            "name": "app",
        },
        "assertions": [
            {
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
        "model": "Schema",
        "description": "Expect the `employees` schema to be created.",
        "filters": {
            "name": "employees",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, schema: set(schema.tables.values_list("name", flat=True)),
                "pass_value": {
                    "employees",
                    "departments",
                    "dept_manager",
                    "dept_emp",
                    "dept_emp_latest_date",
                    "current_dept_emp",
                },
            },
        ]
    },
    {
        "model": "Table",
        "description": "Expect `app.customers` table to be created.",
        "filters": {
            "name": "customers"
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table.schema.name,
                "pass_value": "app",
            },
            {
                "evaluation": lambda datastore, table: table.columns.count(),
                "pass_value": 13,
            },
        ]
    },
    {
        "model": "Table",
        "description": "Expect `employees.departments` table to be created.",
        "filters": {
            "schema__name": "employees",
            "name": "departments"
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: set(table.columns.values_list("name", flat=True)),
                "pass_value": {
                    "dept_no",
                    "dept_name",
                    "started_on",
                },
            },
            {
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "381335ab07d2b67bfe43774716cf7376",
            }
        ]
    },
    {
        "model": "Table",
        "description": "Expect `app.departments` table to be created.",
        "filters": {
            "schema__name": "app",
            "name": "departments"
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: set(table.columns.values_list("name", flat=True)),
                "pass_value": {
                    "id",
                    "dept_name",
                },
            },
            {
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            }
        ]
    },
    {
        "model": "Table",
        "description": "Expect `employees.dept_manager` table to be created.",
        "filters": {
            "schema__name": "employees",
            "name": "dept_manager"
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table.columns.count(),
                "pass_value": 6,
            },
        ]
    },
    {
        "model": "Column",
        "description": "Expect `employees.dept_manager.rating` column to have correct properties.",
        "filters": {
            "table__schema__name": "employees",
            "table__name": "dept_manager",
            "name": "rating",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, column: column.ordinal_position,
                "pass_value": 6,
            },
            {
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "4378e434da68e999650c0beb424da5d4",
            },
            {
                "evaluation": lambda datastore, column: column.default_value,
                "pass_value": "5",
            },
            {
                "evaluation": lambda datastore, column: column.is_primary,
                "pass_value": False,
            },
            {
                "evaluation": lambda datastore, column: column.db_comment,
                "pass_value": "The NPS score for this manager",
            },
        ]
    },
]
