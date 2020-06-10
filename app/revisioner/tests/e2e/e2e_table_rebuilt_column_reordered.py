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
        "description": "The `app`.`departments` table should still exist.",
        "filters": {
            "schema__name": "app",
            "name": "departments",
        },
        "assertions": [
            {
                "summarized": "It should have the same Table identity.",
                "evaluation": lambda datastore, table: table.pk,
                "pass_value": "got35fs8LymV",
            },
            {
                "summarized": "It should have an updated `object_id` value.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "26522",
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
        "description": "tbd.",
        "filters": {
            "table_id": "got35fs8LymV",
            "name": "dept_name",
        },
        "assertions": [
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.pk,
                "pass_value": "H73kDbFONDtX",
            },
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.object_id,
                "pass_value": "26522/3",
            },
        ]
    },
    {
        "model": "Column",
        "description": "tbd.",
        "filters": {
            "table_id": "got35fs8LymV",
            "object_id": "26522/2",
        },
        "assertions": [
            {
                "summarized": "It should have the same Column identity.",
                "evaluation": lambda datastore, column: column.name,
                "pass_value": "category",
            },
        ]
    },
]
