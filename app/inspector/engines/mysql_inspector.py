# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import mysql.connector
import mysql.connector.cursor as cursors


MYSQL_DEFINITIONS_QUERY = """
    SELECT
        c.table_schema,
        CAST(MD5(c.table_schema) AS CHAR) AS schema_object_id,
        c.table_name,
        it.table_id AS table_object_id,
        LOWER(t.table_type) AS table_type,
        CAST(MD5(CONCAT(it.table_id, '/', c.column_name)) AS CHAR) as column_object_id,
        c.column_name,
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
     JOIN information_schema.innodb_tables it
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
    WHERE t.engine = 'InnoDB'
      AND t.table_schema NOT IN ({excluded})
 ORDER BY
      c.table_schema,
      c.table_name,
      c.ordinal_position
"""

MYSQL_INDEXES_QUERY = """
  SELECT DISTINCT
          t.table_schema as schema_name,
          CAST(MD5(t.table_schema) AS CHAR) AS schema_object_id,
          t.table_name as table_name,
          it.table_id as table_object_id,
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
      FROM information_schema.innodb_indexes ix
 LEFT JOIN information_schema.table_constraints tc
        ON ix.name = tc.constraint_name
      JOIN information_schema.innodb_tables it
        ON ix.table_id = it.table_id
      JOIN information_schema.tables t
        ON CONCAT(t.table_schema, '/', t.table_name) = it.name
      JOIN information_schema.innodb_fields f
       ON ix.index_id = f.index_id
    WHERE t.engine = 'InnoDB'
      AND t.table_schema NOT IN ({excluded})
    ORDER BY
      t.table_schema,
      t.table_name,
      ix.index_id,
      f.pos + 1
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

    definitions_sql = MYSQL_DEFINITIONS_QUERY

    indexes_sql = MYSQL_INDEXES_QUERY

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
        result = self.get_first("SELECT VERSION() as version;")
        if len(result):
            return result['version']
        return None
