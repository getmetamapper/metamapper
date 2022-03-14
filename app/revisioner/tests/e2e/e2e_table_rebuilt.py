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


preload_fixtures = ["datastore", "relationships"]

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row["table_object_id"] == "dbcfca725d1ddff7e4505c2f60d02311"
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
                "column_name": "department_name",  # Renamed column
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
        "description": "The `app`.`departments` table should still exist.",
        "filters": {
            "object_ref": "26522",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 2,
            },
            {
                "summarized": "It should retain the same Schema relationship.",
                "evaluation": lambda datastore, table: table.schema.name,
                "pass_value": "app",
            },
            {
                "summarized": "It should retain the same Schema relationship.",
                "evaluation": lambda datastore, table: table.schema.datastore_id,
                "pass_value": "s4N8p5g0wjiS",
            },
            {
                "summarized": "It should retain the same Schema relationship.",
                "evaluation": lambda datastore, table: table.schema_id,
                "pass_value": "f30f68d2909bcd340668d9a0cc8d7c57",
            },
            {
                "summarized": "It should retain the same Table object ID.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`departments` table should have the same columns.",
        "filters": {
            "table__object_ref": "26522",
            "ordinal_position": 1,
        },
        "assertions": [
            {
                "summarized": "It should rename the Column name.",
                "evaluation": lambda datastore, column: column.name,
                "pass_value": "id",
            },
            {
                "summarized": "It should retain the foreign relationship.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
            {
                "summarized": "It should retain the Column metadata.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": "The primary key of the table.",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`departments` table should have the same first column.",
        "filters": {
            "object_ref": "26522/1",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.id,
                "pass_value": 14,
            },
            {
                "summarized": "It should retain the same Table relationship.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
            {
                "summarized": "It should retain the same Comment relationships.",
                "evaluation": lambda datastore, column: column.comments.count() > 0,
                "pass_value": True,
            },
            {
                "summarized": "It retains the same Column metadata.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": "The primary key of the table.",
            },
        ]
    },
    {
        "model": "Column",
        "description": "The `app`.`departments` table should have the same RENAMED second column.",
        "filters": {
            "object_ref": "26522/2",
        },
        "assertions": [
            {
                "summarized": "It should retain the same Table identifier.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
            # TODO(scruwys): These tests fail because we rebuild the table and rename the column.
            {
                "summarized": "It DOES NOT retain the same Column identifier.",
                "evaluation": lambda datastore, column: column.id == 15,
                "pass_value": False,
            },
            {
                "summarized": "It DOES NOT retain the same Comment relationships.",
                "evaluation": lambda datastore, column: column.comments.count() > 0,
                "pass_value": False,
            },
            {
                "summarized": "It DOES NOT retain the same Column metadata.",
                "evaluation": lambda datastore, column: column.short_desc,
                "pass_value": None,
            },
        ]
    },
]
