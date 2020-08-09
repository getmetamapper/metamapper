# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface
import re

import psycopg2
import psycopg2.extras


REDSHIFT_DEFINITIONS_SQL = """
    SELECT
          ns.nspname as table_schema,
          ns.oid::varchar as schema_object_id,
          c.relname as table_name,
          c.oid::varchar as table_object_id,
          CASE WHEN c.relkind = 'r'
               THEN 'table'
               WHEN c.relkind IN ('v', 'm')
               THEN 'view' END AS table_type,
          a.attname AS column_name,
          c.oid || '/' || a.attnum as column_object_id,
          a.attnum AS ordinal_position,
          t.typname AS data_type,
          CASE WHEN NULLIF(a.atttypmod, -1) IS NOT NULL
               THEN NULLIF(a.atttypmod, -1)
               WHEN t.typname = 'timestamp'
               THEN NULL
               ELSE a.attlen END as max_length,
          NULL as numeric_scale,
          CASE WHEN a.attnotnull = true
               THEN FALSE
               ELSE TRUE END AS is_nullable,
          FALSE AS is_primary,
          COALESCE(d.adsrc, '') AS default_value
     FROM pg_class c
     JOIN pg_attribute a
       ON a.attrelid = c.oid
     JOIN pg_type t
       ON a.atttypid = t.oid
     JOIN pg_catalog.pg_namespace AS ns
       ON c.relnamespace = ns.oid
LEFT JOIN pg_attrdef d
       ON c.oid = d.adrelid
      AND a.attnum = d.adnum
    WHERE ns.nspname NOT IN ({excluded})
      AND ns.nspname NOT LIKE 'pg_temp%%'
      AND ns.nspname NOT LIKE 'pg_am%%'
      AND a.attnum > 0
      AND c.relkind in ('r', 'v', 'm')
 ORDER BY ns.nspname, c.relname, a.attnum
"""


class RedshiftInspector(interface.EngineInterface):
    """Access Redshift database metadata.
    """
    sys_schemas = [
        'information_schema',
        'pg_catalog',
        'pg_internal',
    ]

    table_properties = []

    definitions_sql = REDSHIFT_DEFINITIONS_SQL

    connect_timeout_attr = 'connect_timeout'

    @classmethod
    def has_indexes(self):
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
        pattern = r'(Redshift)(\s+)([\d.]+)'
        result = self.get_first("SELECT VERSION() as version")
        if len(result):
            matches = re.findall(pattern, result['version'])
            if len(matches) and len(matches[0]) == 3:
                return matches[0][2]
        return None

    def get_indexes(self, *args, **kwargs):
        """Retrieve indexes from the database.
        """
        return []
