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


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16522
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

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16522
        ),
    },
])

inspected_indexes += [
    {
        "schema_name": "app",
        "schema_object_id": 16441,
        "table_name": "departments",
        "table_object_id": 26522,
        "index_name": "departments_dept_name_key",
        "index_object_id": 26528,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX departments_dept_name_key ON app.departments USING btree (dept_name)",
        "columns": [
            {
                "column_name": "dept_name",
                "ordinal_position": 1
            }
        ]
    }
]

test_cases = [
    {
        "model": "Table",
        "description": "The `app.departments` table should no longer have the old `object_id`.",
        "filters": {
            "object_id": "16522",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, table: table is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `app.departments` index should no longer have the old `object_id`.",
        "filters": {
            "object_id": "16528",
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
            "object_id": "26522",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": "got35fs8LymV",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app.departments` should have the same Column objects.",
        "filters": {
            "object_id": "26522/1",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": "jeGFqE06Mp06",
            },
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "got35fs8LymV",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app.departments` should have the same Column objects.",
        "filters": {
            "object_id": "26522/2",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": "H73kDbFONDtX",
            },
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "got35fs8LymV",
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `departments_dept_name_key` index should not have the old `object_id`.",
        "filters": {
            "object_id": "16528",
        },
        "assertions": [
            {
                "evaluation": lambda datastore, index: index is None,
                "pass_value": True,
            },
        ]
    },
    {
        "model": "Index",
        "description": "The `departments_dept_name_key` index should still exist.",
        "filters": {
            "object_id": "26528",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Index identifier.",
                "evaluation": lambda datastore, index: index.pk,
                "pass_value": "1Gl5bDQRAk4B",
            },
        ]
    },
    {
        "model": "IndexColumn",
        "description": "The `departments_dept_name_key` index should still exist.",
        "filters": {
            "index_id": "1Gl5bDQRAk4B",
        },
        "assertions": [
            {
                "summarized": "It should retain the same IndexColumn.",
                "evaluation": lambda datastore, index_column: index_column.pk,
                "pass_value": 9,
            },
            {
                "summarized": "It should retain the same IndexColumn.column_id.",
                "evaluation": lambda datastore, index_column: index_column.column_id,
                "pass_value": "H73kDbFONDtX",
            },
        ]
    },
]
