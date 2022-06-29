# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import psycopg2
import psycopg2.extras


POSTGRESQL_DEFINITIONS_SQL = """
WITH primary_key AS (
  SELECT c.table_schema, c.table_name, c.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.constraint_column_usage AS ccu
   USING (constraint_schema, constraint_name)
    JOIN information_schema.columns AS c
      ON c.table_schema = tc.constraint_schema
     AND tc.table_name = c.table_name
     AND ccu.column_name = c.column_name
   WHERE constraint_type = 'PRIMARY KEY'
)
    SELECT
          c.table_schema,
          c.table_schema::regnamespace::oid AS schema_object_id,
          c.table_name,
          to_regclass(c.table_schema || '.' || c.table_name)::oid AS table_object_id,
          LOWER(t.table_type) AS table_type,
          to_regclass(c.table_schema || '.' || c.table_name)::oid || '/' || c.ordinal_position AS column_object_id,
          c.column_name,
          pg_catalog.col_description(
            to_regclass(c.table_schema || '.' || c.table_name)::oid,
            c.ordinal_position
          ) as column_description,
          c.ordinal_position,
          c.data_type,
          CASE WHEN c.character_maximum_length IS NOT NULL
               THEN c.character_maximum_length
               ELSE c.numeric_precision END AS max_length,
          c.numeric_scale,
          CASE WHEN UPPER(c.is_nullable) = 'YES'
               THEN TRUE
               ELSE FALSE END AS is_nullable,
          CASE WHEN pk.column_name IS NOT NULL
               THEN TRUE
               ELSE FALSE END AS is_primary,
          COALESCE(c.column_default, '') AS default_value
     FROM information_schema.columns c
     JOIN information_schema.tables t
       ON c.table_schema = t.table_schema
      AND c.table_name = t.table_name
LEFT JOIN primary_key pk
       ON c.table_schema = pk.table_schema
      AND c.table_name = pk.table_name
      AND c.column_name = pk.column_name
    WHERE c.table_schema NOT IN ({excluded})
 ORDER BY c.table_schema, c.table_name, c.ordinal_position
"""

POSTGRESQL_INDEXES_SQL = """
    SELECT DISTINCT
          ui.schemaname AS schema_name,
          ui.schemaname::regnamespace::oid AS schema_object_id,
          t.relname AS table_name,
          t.oid AS table_object_id,
          ix.relname AS index_name,
          ix.oid AS index_object_id,
          indisunique AS is_unique,
          indisprimary AS is_primary,
          a.attname AS column_name,
          array_position(string_to_array(i.indkey::text, ' '), a.attnum::text) AS ordinal_position,
          pg_get_indexdef(i.indexrelid) AS definition
     FROM pg_index i
     JOIN pg_class t
       ON t.oid = i.indrelid
     JOIN pg_class ix
       ON ix.oid = i.indexrelid
LEFT JOIN pg_stat_user_indexes ui
       ON ui.indexrelid = i.indexrelid
LEFT JOIN pg_attribute a
       ON a.attrelid = i.indrelid
      AND a.attnum = ANY(i.indkey)
      AND a.attnum > 0
    WHERE ui.schemaname NOT IN ({excluded})
"""


class PostgresqlInspector(interface.EngineInterface):
    """Access Postgres database metadata.
    """
    sys_schemas = [
        'information_schema',
        'pg_catalog',
        'pg_toast',
    ]

    table_properties = []

    definitions_sql = POSTGRESQL_DEFINITIONS_SQL

    indexes_sql = POSTGRESQL_INDEXES_SQL

    connect_timeout_attr = 'connect_timeout'

    @classmethod
    def has_checks(self):
        return True

    @classmethod
    def has_indexes(self):
        return True

    @classmethod
    def has_partitions(self):
        return False

    @classmethod
    def has_usage(self):
        return False

    @property
    def connector(self):
        return psycopg2

    @property
    def dictcursor(self):
        return psycopg2.extras.RealDictCursor

    @property
    def cursor_kwargs(self):
        return {'cursor_factory': self.dictcursor}

    def get_db_version(self):
        result = self.get_first('SHOW server_version;')
        if len(result):
            return result['server_version']
        return None
