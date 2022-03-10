"""
Create a schema with some tables.

Example SQL:

  CREATE SCHEMA `public`;
  CREATE TABLE `public`.`workspaces` ...

We include a few random actions on other tables to ensure no conflicts.
"""
from app.revisioner.tests.e2e import inspected
from app.revisioner.tests.test_e2e import mutate_inspected


preload_fixtures = ['datastore']

inspected_tables = mutate_inspected(inspected.tables_and_views, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['schema_object_id'] == 16441
        ),
    },
])

inspected_tables += [
    {
        "schema_object_id": 2200,
        "table_schema": "public",
        "table_object_id": 24725,
        "table_name": "groups",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "24725/1",
                "column_name": "id",
                "column_description": None,
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": "nextval('groups_id_seq'::regclass)"
            },
            {
                "column_object_id": "24725/2",
                "column_name": "group_name",
                "column_description": None,
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 255,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "24725/3",
                "column_name": "created_at",
                "column_description": None,
                "ordinal_position": 3,
                "data_type": "timestamp without time zone",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": "CURRENT_TIMESTAMP"
            }
        ]
    },
    {
        "schema_object_id": 2200,
        "table_schema": "public",
        "table_object_id": 24737,
        "table_name": "permissions",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "24737/1",
                "column_name": "user_id",
                "column_description": None,
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "24737/2",
                "column_name": "group_id",
                "column_description": None,
                "ordinal_position": 2,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "24737/3",
                "column_name": "role",
                "column_description": None,
                "ordinal_position": 3,
                "data_type": "character varying",
                "max_length": 255,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": "'BASIC'::character varying"
            },
            {
                "column_object_id": "24737/4",
                "column_name": "granted_at",
                "column_description": None,
                "ordinal_position": 4,
                "data_type": "timestamp without time zone",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": "CURRENT_TIMESTAMP"
            }
        ]
    },
    {
        "schema_object_id": 2200,
        "table_schema": "public",
        "table_object_id": 24714,
        "table_name": "users",
        "table_type": "base table",
        "properties": {},
        "columns": [
            {
                "column_object_id": "24714/1",
                "column_name": "id",
                "column_description": None,
                "ordinal_position": 1,
                "data_type": "integer",
                "max_length": 32,
                "numeric_scale": 0,
                "is_nullable": False,
                "is_primary": True,
                "default_value": "nextval('users_id_seq'::regclass)"
            },
            {
                "column_object_id": "24714/2",
                "column_name": "email",
                "column_description": None,
                "ordinal_position": 2,
                "data_type": "character varying",
                "max_length": 255,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": ""
            },
            {
                "column_object_id": "24714/3",
                "column_name": "created_at",
                "column_description": None,
                "ordinal_position": 3,
                "data_type": "timestamp without time zone",
                "max_length": None,
                "numeric_scale": None,
                "is_nullable": False,
                "is_primary": False,
                "default_value": "CURRENT_TIMESTAMP"
            }
        ]
    },
]

column_fields = [
    "name",
    "object_id",
    "ordinal_position",
    "data_type",
    "max_length",
    "numeric_scale",
    "is_nullable",
    "is_primary",
    "default_value",
]

test_cases = [
    {
        "description": "Expect first time created columns to be dropped from the revision logs.",
        "assertions": [
            {
                "evaluation": lambda datastore, nulled: datastore.most_recent_run.revisions.filter(action=1, resource_type__model='column').count(),
                "pass_value": 0,
            },
        ]
    },
    {
        "model": "Schema",
        "description": "The `public` schema should be created.",
        "filters": {
            "name": "public",
        },
        "assertions": [
            {
                "summarized": "It should be part of the Datastore.",
                "evaluation": lambda datastore, schema: schema.datastore_id == datastore.pk,
                "pass_value": True,
            },
            {
                "summarized": "It should retain the `object_id` value.",
                "evaluation": lambda datastore, schema: schema.object_id,
                "pass_value": "2200",
            },
            {
                "summarized": "It should create the three schemas mentioned.",
                "evaluation": lambda datastore, schema: set(schema.tables.values_list("name", flat=True)),
                "pass_value": {"users", "permissions", "groups"},
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `public`.`users` table should be created.",
        "filters": {
            "schema__name": "public",
            "name": "users",
        },
        "assertions": [
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": lambda datastore, table: table.object_id,
                "pass_value": "24714",
            },
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": (
                    lambda d, table: list(table.columns.order_by('ordinal_position').values(*column_fields))
                ),
                "pass_value": [
                    {
                        "name": "id",
                        "object_id": "24714/1",
                        "ordinal_position": 1,
                        "data_type": "integer",
                        "max_length": 32,
                        "numeric_scale": 0,
                        "is_nullable": False,
                        "is_primary": True,
                        "default_value": "nextval('users_id_seq'::regclass)"
                    },
                    {
                        "name": "email",
                        "object_id": "24714/2",
                        "ordinal_position": 2,
                        "data_type": "character varying",
                        "max_length": 255,
                        "numeric_scale": None,
                        "is_nullable": False,
                        "is_primary": False,
                        "default_value": ""
                    },
                    {
                        "name": "created_at",
                        "object_id": "24714/3",
                        "ordinal_position": 3,
                        "data_type": "timestamp without time zone",
                        "max_length": None,
                        "numeric_scale": None,
                        "is_nullable": False,
                        "is_primary": False,
                        "default_value": "CURRENT_TIMESTAMP"
                    }
                ],
            },
        ]
    },
    {
        "model": "Table",
        "description": "The `public`.`groups` table should be created.",
        "filters": {
            "schema__name": "public",
            "name": "groups",
        },
        "assertions": [
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": lambda d, table: table.object_id,
                "pass_value": "24725",
            },
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": (
                    lambda d, table: list(table.columns.order_by('ordinal_position').values(*column_fields))
                ),
                "pass_value": [
                    {
                        "name": "id",
                        "object_id": "24725/1",
                        "ordinal_position": 1,
                        "data_type": "integer",
                        "max_length": 32,
                        "numeric_scale": 0,
                        "is_nullable": False,
                        "is_primary": True,
                        "default_value": "nextval('groups_id_seq'::regclass)"
                    },
                    {
                        "name": "group_name",
                        "object_id": "24725/2",
                        "ordinal_position": 2,
                        "data_type": "character varying",
                        "max_length": 255,
                        "numeric_scale": None,
                        "is_nullable": False,
                        "is_primary": False,
                        "default_value": ""
                    },
                    {
                        "name": "created_at",
                        "object_id": "24725/3",
                        "ordinal_position": 3,
                        "data_type": "timestamp without time zone",
                        "max_length": None,
                        "numeric_scale": None,
                        "is_nullable": False,
                        "is_primary": False,
                        "default_value": "CURRENT_TIMESTAMP"
                    }
                ],
            },
        ]
    },
]
