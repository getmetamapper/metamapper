"""
Drop a table (`app`.`departments`) and re-create it with the same name.

Example SQL:

  CREATE TABLE `tmp`.`departments` (LIKE `app`.`departments`);
  DROP TABLE `app`.`departments`;
  ALTER TABLE `tmp`.`departments` RENAME `app`.`departments`;

We would expect the table and it's children to maintain the same internal identifiers.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ["datastore"]

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row["table_object_id"] == "381335ab07d2b67bfe43774716cf7376"
        ),
    },
])

inspected_tables += [
    {
        "schema_object_id": 16441,
        "table_schema": "app",
        "table_object_id": 26522,
        "table_name": "departments",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "26522/1",
                "column_name": "id",
                "column_description": None,
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": "nextval('app.departments_id_seq'::regclass)"
            },
            {
                "column_object_id": "26522/2",
                "column_name": "dept_name",
                "column_description": None,
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 40,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            }
        ]
    }
]

test_cases = [
    {
        "model": "Table",
        "description": "The `app.departments` table should no longer have the old `object_id`.",
        "filters": {
            "object_ref": "16522",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `app.departments` table should still exist.",
        "filters": {
            "object_ref": "26522",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 2,
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app.departments` should have the same Column objects.",
        "filters": {
            "object_ref": "26522/1",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": 14,
            },
            {
                "summarized": "It should retain the same Table relationship.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app.departments` should have the same Column objects.",
        "filters": {
            "object_ref": "26522/2",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": 15,
            },
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
        ]
    },
]
