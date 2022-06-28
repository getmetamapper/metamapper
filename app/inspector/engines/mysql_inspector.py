# -*- coding: utf-8 -*-
import mysql.connector
import mysql.connector.cursor as cursors

import re
import app.inspector.engines.interface as interface


MYSQL_V5_REGEXP = re.compile(r'5\.[0-9]{1,3}\.[0-9]{1,3}')

MYSQL_DEFINITIONS_SQL = """
    SELECT
        c.table_schema,
        CAST(MD5(c.table_schema) AS CHAR) AS schema_object_id,
        c.table_name,
        IFNULL(it.table_id, CAST(MD5(CONCAT(c.table_schema, '/', c.table_name)) AS CHAR)) AS table_object_id,
        LOWER(t.table_type) AS table_type,
        CAST(MD5(CONCAT(
          IFNULL(it.table_id, CAST(MD5(CONCAT(c.table_schema, '/', c.table_name)) AS CHAR)),
          '/',
          c.column_name
        )) AS CHAR) as column_object_id,
        c.column_name,
        c.column_comment AS column_description,
        c.ordinal_position,
        c.data_type,
        CASE WHEN c.character_maximum_length IS NOT NULL
             THEN c.character_maximum_length
             ELSE c.numeric_precision END as max_length,
        c.numeric_scale,
        CASE WHEN UPPER(c.is_nullable) = 'YES'
             THEN TRUE
             ELSE FALSE END AS is_nullable,
        CASE WHEN pk.column_name IS NOT NULL
             THEN TRUE
             ELSE FALSE END AS is_primary,
        COALESCE(c.column_default, '') as default_value
     FROM information_schema.columns c
     JOIN information_schema.tables t
       ON c.table_schema = t.table_schema
      AND c.table_name = t.table_name
LEFT JOIN information_schema.{innodb_prefix}_tables it
       ON CONCAT(c.table_schema, '/', c.table_name) = it.name
LEFT JOIN (
   SELECT t.table_schema, t.table_name, k.column_name
     FROM information_schema.table_constraints t
     JOIN information_schema.key_column_usage k
    USING (constraint_name,table_schema,table_name)
    WHERE t.constraint_type = 'PRIMARY KEY'
  ) pk
      ON c.table_schema = pk.table_schema
     AND c.table_name = pk.table_name
     AND c.column_name = pk.column_name
   WHERE t.table_schema NOT IN ({excluded})
ORDER BY c.table_schema, c.table_name, c.ordinal_position
"""

MYSQL_INDEXES_SQL = """
  SELECT DISTINCT
          t.table_schema as schema_name,
          CAST(MD5(t.table_schema) AS CHAR) AS schema_object_id,
          t.table_name as table_name,
          IFNULL(it.table_id, CAST(MD5(CONCAT(t.table_schema, '/', t.table_name)) AS CHAR)) AS table_object_id,
          CASE WHEN UPPER(ix.name) = 'PRIMARY'
               THEN CONCAT('idx_pk_', t.table_name)
               ELSE ix.name END AS index_name,
          ix.index_id AS index_object_id,
          CASE WHEN UPPER(tc.constraint_type) = 'UNIQUE'
               THEN TRUE
               ELSE FALSE END AS is_unique,
          CASE WHEN UPPER(tc.constraint_type) = 'PRIMARY KEY'
               THEN TRUE
               ELSE FALSE END AS is_primary,
          f.name as column_name,
          f.pos + 1 as ordinal_position,
          NULL as definition
      FROM information_schema.{innodb_prefix}_indexes ix
 LEFT JOIN information_schema.table_constraints tc
        ON ix.name = tc.constraint_name
      JOIN information_schema.{innodb_prefix}_tables it
        ON ix.table_id = it.table_id
      JOIN information_schema.tables t
        ON CONCAT(t.table_schema, '/', t.table_name) = it.name
      JOIN information_schema.{innodb_prefix}_fields f
        ON ix.index_id = f.index_id
     WHERE t.table_schema NOT IN ({excluded})
"""


class MySQLInspector(interface.EngineInterface):
    """Access MySQL database metadata.
    """
    sys_schemas = [
        'information_schema',
        'mysql',
        'performance_schema',
        'sys',
    ]

    table_properties = []

    definitions_sql = MYSQL_DEFINITIONS_SQL

    indexes_sql = MYSQL_INDEXES_SQL

    connect_timeout_attr = 'connect_timeout'

    @classmethod
    def has_indexes(self):
        return True

    @property
    def connector(self):
        return mysql.connector

    @property
    def dictcursor(self):
        return cursors.MySQLCursorDict

    @property
    def cursor_kwargs(self):
        return {'cursor_class': self.dictcursor}

    def get_db_version(self):
        result = self.get_first('SELECT VERSION() as version;')
        if len(result):
            return result['version']
        return None

    def get_tables_and_views_sql(self, excluded_schemas):
        """Generate SQL statement for getting tables and views.
        """
        return self.definitions_sql.format(
            excluded=', '.join(['%s'] * len(excluded_schemas)),
            innodb_prefix='innodb_sys' if MYSQL_V5_REGEXP.match(self.version or '') else 'innodb',
        )

    def get_indexes_sql(self, excluded_schemas):
        """Generate SQL statement for getting indexes and constraints.
        """
        return self.indexes_sql.format(
            excluded=', '.join(['%s'] * len(excluded_schemas)),
            innodb_prefix='innodb_sys' if MYSQL_V5_REGEXP.match(self.version or '') else 'innodb',
        )
