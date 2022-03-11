"""
Drop a table (`app`.`departments`) and re-create it with the
same name. However, the underlying column structure has slightly changed.

Example SQL:

  DROP TABLE `app`.`departments`;
  CREATE TABLE `app`.`departments` (
    id SERIAL NOT NULL,
    category  VARCHAR(40) NOT NULL,
    dept_name  VARCHAR(40) NOT NULL,
    dept_head  INT NOT NULL,
    PRIMARY KEY (id),
    UNIQUE      (dept_name)
  );

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
                "column_name": "category",
                "column_description": None,
                "ordinal_position": 2,
                "data_type": "varchar",
                "max_length": 255,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": True,
                "default_value": ""
            },
            {
                "column_object_id": "26522/3",
                "column_name": "dept_name",
                "column_description": None,
                "ordinal_position": 3,
                "data_type": "character varying",
                "max_length": 40,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "26522/4",
                "column_name": "dept_head",
                "column_description": None,
                "ordinal_position": 3,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": True,
                "is_primary": False,
                "default_value": ""
            }
        ]
    }
]

test_cases = [
    {
        "model": "Table",
        "description": "The `app`.`departments` table should still exist.",
        "filters": {
            "schema__name": "app",
            "name": "departments",
        },
        "assertions": [
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": 2,
            },
            {
                "summarized": "It should have an updated `object_id` value.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
            {
                "summarized": "It should have the expected columns.",
                "evaluation": lambda datastore, table: set(table.columns.values_list("name", flat=True)),
                "pass_value": {
                    "id",
                    "category",
                    "dept_name",
                    "dept_head",
                },
            },
        ]
    },
    {
        "model": "Column",
        "description": "The related columns should be preserved.",
        "filters": {
            "table_id": "dbcfca725d1ddff7e4505c2f60d02311",
            "name": "dept_name",
        },
        "assertions": [
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": 15,
            },
            {
                "summarized": "It should have the same Column position.",
                "evaluation": lambda datastore, column: column.ordinal_position,
                "pass_value": 3,
            },
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "e736e9c9159e9930a9a69e7c0ae0c58b",
            },
        ]
    },
    {
        "model": "Column",
        "filters": {
            "object_id": "1274389cceee476f21e0763bbb606856",
        },
        "assertions": [
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.name,
                "pass_value": "category",
            },
            {
                "summarized": "It should have the same Table relationship.",
                "evaluation": lambda datastore, column: column.table_id,
                "pass_value": "dbcfca725d1ddff7e4505c2f60d02311",
            },
        ]
    },
]
