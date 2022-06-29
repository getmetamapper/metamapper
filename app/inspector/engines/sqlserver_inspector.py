# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import pymssql


SQLSERVER_DEFINITION_QUERY = """
WITH primary_key AS (
  SELECT c.table_schema, c.table_name, c.column_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.constraint_column_usage AS ccu
      ON ccu.constraint_schema = tc.constraint_schema
     AND ccu.constraint_name = tc.constraint_name
    JOIN information_schema.columns AS c
      ON c.table_schema = tc.constraint_schema
     AND tc.table_name = c.table_name
     AND ccu.column_name = c.column_name
   WHERE constraint_type = 'PRIMARY KEY'
)
  SELECT DISTINCT
      SCHEMA_NAME(t.schema_id) AS table_schema,
      t.schema_id AS schema_object_id,
      t.name AS table_name,
      t.object_id AS table_object_id,
      CASE WHEN UPPER(t.type) = 'U'
           THEN 'base table'
           WHEN UPPER(t.type) = 'V'
           THEN 'view' END AS table_type,
      CONCAT(t.object_id, '/', c.column_id) AS column_object_id,
      c.name as column_name,
      CAST(PROP_COL.VALUE AS NVARCHAR(MAX))  as column_description,
      ic.ordinal_position,
      LOWER(ic.data_type) as data_type,
      CASE WHEN c.max_length IS NOT NULL
           THEN c.max_length
           ELSE c.precision END AS max_length,
      c.scale as numeric_scale,
      c.is_nullable,
      CASE WHEN pk.column_name IS NOT NULL
           THEN 1
           ELSE 0 END AS is_primary,
      COALESCE(ic.column_default, '') AS default_value
     FROM sys.columns c
     JOIN sys.objects t
       ON c.object_id = t.object_id
     JOIN information_schema.columns ic
       ON LOWER(ic.table_schema) = LOWER(SCHEMA_NAME(t.schema_id))
      AND LOWER(ic.table_name) = LOWER(t.name)
      AND LOWER(ic.column_name) = LOWER(c.name)
LEFT JOIN primary_key pk
       ON LOWER(SCHEMA_NAME(t.schema_id)) = LOWER(pk.table_schema)
      AND LOWER(t.name) = LOWER(pk.table_name)
      AND LOWER(c.name) = LOWER(pk.column_name)
LEFT JOIN SYS.EXTENDED_PROPERTIES PROP_COL
       ON prop_col.MAJOR_ID = OBJECT_ID(ic.table_schema + '.' + ic.table_name)
      AND prop_col.MINOR_ID = ic.ordinal_position
      AND prop_col.NAME = 'MS_Description'
    WHERE LOWER(SCHEMA_NAME(t.schema_id)) NOT IN ({excluded})
      AND UPPER(t.type) IN ('U', 'V')
 ORDER BY SCHEMA_NAME(t.schema_id), t.name, ic.ordinal_position
"""


SQLSERVER_INDEXES_QUERY = """
  SELECT DISTINCT
    SCHEMA_NAME(t.schema_id) as schema_name,
    t.schema_id as schema_object_id,
    t.name as table_name,
    t.object_id as table_object_id,
    i.name as index_name,
    CONCAT(t.object_id, '/', i.index_id) as index_object_id,
    i.is_unique,
    i.is_primary_key as is_primary,
    col.name as column_name,
    ic.key_ordinal as ordinal_position,
    NULL as definition
 FROM sys.objects t
 JOIN sys.indexes i
   ON t.object_id = i.object_id
 JOIN sys.index_columns ic
   ON ic.object_id = t.object_id
  AND ic.index_id = i.index_id
 JOIN sys.columns col
   ON ic.object_id = col.object_id
  AND ic.column_id = col.column_id
WHERE LOWER(SCHEMA_NAME(t.schema_id)) NOT IN ({excluded})
  AND UPPER(t.type) IN ('U', 'V')
"""


class SQLServerInspector(interface.EngineInterface):
    """Access Microsoft SQL Server database metadata.
    """
    sys_schemas = [
        'information_schema',
        'sys',
    ]

    table_properties = []

    definitions_sql = SQLSERVER_DEFINITION_QUERY

    indexes_sql = SQLSERVER_INDEXES_QUERY

    connect_timeout_attr = 'login_timeout'

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
        return pymssql

    @property
    def dictcursor(self):
        return None

    @property
    def cursor_kwargs(self):
        return {'as_dict': True}

    @property
    def connect_kwargs(self):
        """Override connection kwargs per https://github.com/pymssql/pymssql/issues/339#issuecomment-165740512
        """
        _kwargs = {
            'host': self.host,
            'user': self.username,
            'password': self.password,
            'port': self.port,
            'database': self.database,
            'conn_properties': '',
        }
        if self.connect_timeout_attr is not None:
            _kwargs[self.connect_timeout_attr] = self.connect_timeout_value
        return _kwargs

    def get_db_version(self):
        result = self.get_first(
            "SELECT SERVERPROPERTY('BuildClrVersion') as version"
        )
        if len(result):
            version = result['version']
            if isinstance(version, (bytes,)):
                version = version.decode()
            return version
        return None
