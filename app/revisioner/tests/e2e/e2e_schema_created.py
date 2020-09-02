"""
Create a schema with some tables and indexes.

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

inspected_indexes = mutate_inspected(inspected.indexes, [
    {
        "type": "dropped",
        "filters": (
            lambda row: row['table_object_id'] == 16441
        ),
    },
])

inspected_indexes += [
    {
        "schema_name": "public",
        "schema_object_id": 2200,
        "table_name": "groups",
        "table_object_id": 24725,
        "index_name": "groups_group_name_key",
        "index_object_id": 24732,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX groups_group_name_key ON public.groups USING btree (group_name)",
        "columns": [
            {
                "column_name": "group_name",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "public",
        "schema_object_id": 2200,
        "table_name": "groups",
        "table_object_id": 24725,
        "index_name": "groups_pkey",
        "index_object_id": 24730,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX groups_pkey ON public.groups USING btree (id)",
        "columns": [
            {
                "column_name": "id",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "public",
        "schema_object_id": 2200,
        "table_name": "permissions",
        "table_object_id": 24737,
        "index_name": "permissions_user_id_group_id_role_key",
        "index_object_id": 24742,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX permissions_user_id_group_id_role_key ON public.permissions USING btree (user_id, group_id, role)",
        "columns": [
            {
                "column_name": "user_id",
                "ordinal_position": 1
            },
            {
                "column_name": "group_id",
                "ordinal_position": 2
            },
            {
                "column_name": "role",
                "ordinal_position": 3
            }
        ]
    },
    {
        "schema_name": "public",
        "schema_object_id": 2200,
        "table_name": "users",
        "table_object_id": 24714,
        "index_name": "users_email_key",
        "index_object_id": 24721,
        "is_unique": True,
        "is_primary": False,
        "definition": "CREATE UNIQUE INDEX users_email_key ON public.users USING btree (email)",
        "columns": [
            {
                "column_name": "email",
                "ordinal_position": 1
            }
        ]
    },
    {
        "schema_name": "public",
        "schema_object_id": 2200,
        "table_name": "users",
        "table_object_id": 24714,
        "index_name": "users_pkey",
        "index_object_id": 24719,
        "is_unique": True,
        "is_primary": True,
        "definition": "CREATE UNIQUE INDEX users_pkey ON public.users USING btree (id)",
        "columns": [
            {
                "column_name": "id",
                "ordinal_position": 1
            }
        ]
    }
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

index_fields = [
    "table__name",
    "name",
    "object_id",
    "is_unique",
    "is_primary",
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
        "model": "Index",
        "description": "The `public`.`permissions_user_id_group_id_role_key` index should be created.",
        "filters": {
            "table__schema__name": "public",
            "object_id": "24742",
        },
        "assertions": [
            {
                "summarized": "It should have the correct index name.",
                "evaluation": lambda datastore, index: index.name,
                "pass_value": "permissions_user_id_group_id_role_key",
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
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": (
                    lambda d, table: list(table.indexes.order_by('object_id').values(*index_fields))
                ),
                "pass_value": [
                    {
                        "table__name": "users",
                        "name": "users_pkey",
                        "object_id": "24719",
                        "is_unique": True,
                        "is_primary": True,
                    },
                    {
                        "table__name": "users",
                        "name": "users_email_key",
                        "object_id": "24721",
                        "is_unique": True,
                        "is_primary": False,
                    },
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
            {
                "summarized": "It should have the correct `object_id` value.",
                "evaluation": (
                    lambda d, table: list(table.indexes.order_by('object_id').values(*index_fields))
                ),
                "pass_value": [
                    {
                        "table__name": "groups",
                        "name": "groups_pkey",
                        "object_id": "24730",
                        "is_unique": True,
                        "is_primary": True,
                    },
                    {
                        "table__name": "groups",
                        "name": "groups_group_name_key",
                        "object_id": "24732",
                        "is_unique": True,
                        "is_primary": False,
                    },
                ],
            },
        ]
    },
]
