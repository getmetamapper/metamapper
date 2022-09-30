# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import cx_Oracle


ORACLE_DEFINITIONS_SQL = """
WITH METAMAPPER_USERS AS (
  SELECT u.USER_ID, u.USERNAME
    FROM DBA_USERS u
   WHERE EXISTS (SELECT 1 FROM dba_objects o WHERE o.owner = u.username)
     AND DEFAULT_TABLESPACE NOT IN ({excluded})
     AND ACCOUNT_STATUS = 'OPEN'
),
PRIMARY_KEYS AS (
  SELECT DISTINCT COLS.COLUMN_NAME, COLS.TABLE_NAME, COLS.OWNER
    FROM ALL_CONS_COLUMNS COLS
    JOIN ALL_CONSTRAINTS CONS
     ON CONS.CONSTRAINT_NAME = COLS.CONSTRAINT_NAME
    AND CONS.OWNER = COLS.OWNER
    AND UPPER(CONS.CONSTRAINT_TYPE) = 'P'
)
SELECT DISTINCT
    T.OWNER AS table_schema,
    U.USER_ID AS schema_object_id,
    T.OBJECT_NAME AS table_name,
    LOWER(T.OBJECT_TYPE) AS table_type,
    T.OBJECT_ID AS table_object_id,
    CONCAT(CONCAT(T.OBJECT_ID, '/'), C.COLUMN_ID) AS column_object_id,
    C.COLUMN_NAME AS column_name,
    CO.COMMENTS AS column_description,
    C.COLUMN_ID AS ordinal_position,
    C.DATA_TYPE AS data_type,
    CASE WHEN C.DATA_LENGTH IS NOT NULL
         THEN C.DATA_LENGTH
         ELSE C.DATA_PRECISION END AS max_length,
    C.DATA_SCALE AS numeric_scale,
    CASE WHEN C.NULLABLE = 'Y'
         THEN 1
         ELSE 0 END AS is_nullable,
    CASE WHEN PKS.COLUMN_NAME IS NOT NULL
         THEN 1
         ELSE 0 END AS is_primary,
    NULL AS default_value
  FROM DBA_OBJECTS T
  JOIN ALL_TAB_COLS C
    ON C.TABLE_NAME = T.OBJECT_NAME
   AND C.OWNER = T.OWNER
  LEFT JOIN METAMAPPER_USERS U
    ON U.USERNAME = T.OWNER
  LEFT JOIN PRIMARY_KEYS PKS
    ON PKS.COLUMN_NAME = C.COLUMN_NAME
   AND PKS.TABLE_NAME = C.TABLE_NAME
   AND PKS.OWNER = C.OWNER
  LEFT JOIN ALL_COL_COMMENTS CO
    ON CO.TABLE_NAME = C.TABLE_NAME
   AND CO.OWNER = C.OWNER
   AND CO.COLUMN_NAME = C.COLUMN_NAME
 WHERE LOWER(T.OBJECT_TYPE) IN ('table', 'view')
   AND LOWER(T.OWNER) NOT IN ({excluded})
 ORDER BY T.OWNER, T.OBJECT_NAME, C.COLUMN_ID
"""

ORACLE_INDEXES_SQL = """
WITH METAMAPPER_USERS AS (
  SELECT u.USER_ID, u.USERNAME
    FROM DBA_USERS u
   WHERE EXISTS (SELECT 1 FROM dba_objects o WHERE o.owner = u.username)
     AND DEFAULT_TABLESPACE NOT IN ({excluded})
     AND ACCOUNT_STATUS = 'OPEN'
)
SELECT
      I.OWNER AS schema_name,
      U.USER_ID AS schema_object_id,
      T.OBJECT_NAME AS table_name,
      T.OBJECT_ID AS table_object_id,
      I.OBJECT_NAME AS index_name,
      I.OBJECT_ID AS index_object_id,
      CASE WHEN UPPER(CONS.CONSTRAINT_TYPE) = 'P'
           THEN 1
           ELSE 0 END AS is_primary,
      CASE WHEN UPPER(IDX.UNIQUENESS) = 'UNIQUE'
           THEN 1
           ELSE 0 END AS is_unique,
      IC.COLUMN_NAME AS column_name,
      IC.COLUMN_POSITION AS ordinal_position
     FROM DBA_OBJECTS I
     JOIN METAMAPPER_USERS U
       ON U.USERNAME = I.OWNER
LEFT JOIN ALL_INDEXES IDX
       ON IDX.INDEX_NAME = I.OBJECT_NAME
      AND IDX.OWNER = I.OWNER
LEFT JOIN DBA_OBJECTS T
       ON T.OBJECT_NAME = IDX.TABLE_NAME
      AND T.OWNER = IDX.OWNER
LEFT JOIN ALL_IND_COLUMNS IC
       ON IC.INDEX_NAME = I.OBJECT_NAME
      AND IC.INDEX_OWNER = I.OWNER
LEFT JOIN ALL_CONSTRAINTS CONS
       ON CONS.CONSTRAINT_NAME = I.OBJECT_NAME
      AND CONS.OWNER = I.OWNER
      AND UPPER(CONS.CONSTRAINT_TYPE) = 'P'
    WHERE LOWER(I.OBJECT_TYPE) IN ('index')
      AND LOWER(I.OWNER) NOT IN ({excluded})
"""


class DictCursor(cx_Oracle.Cursor):
    """Override Oracle Cursor to create dictionaries.
    """
    def fetchone(self):
        return self.as_dict(self.columns, super().fetchone())

    def fetchall(self):
        return [
            self.as_dict(self.columns, r) for r in super().fetchall()
        ]

    def fetchmany(self, size=1000):
        return [
            self.as_dict(self.columns, r) for r in super().fetchmany(size)
        ]

    @property
    def columns(self):
        return list(map(lambda d: d[0].lower(), self.description))

    def as_dict(self, columns, args):
        return dict(zip(columns, args))


class Connection(cx_Oracle.Connection):
    """Override Oracle Connection object to take individual parameters.
    """
    def __init__(self, host, user, password, port, database):
        """Make DSN parameter string and pass as connection.
        """
        dsn = cx_Oracle.makedsn(host, port, sid=database)
        return super(Connection, self).__init__(
            '{user}/{password}@{dsn}'.format(**locals())
        )

    def cursor(self):
        return DictCursor(self)


class ConnectionFactory(object):
    """Factory function for building connections.
    """
    @classmethod
    def connect(cls, **kwargs):
        return Connection(**kwargs)


class OracleInspector(interface.EngineInterface):
    """Access Oracle database metadata.
    """
    sys_schemas = [
        'apex_030200',
        'apex_050000',
        'appqossys',
        'audsys',
        'ctxsys',
        'dbsfwuser',
        'dbsnmp',
        'dvsys',
        'exfsys',
        'flows_files',
        'gsmadmin_internal',
        'lbacsys',
        'mdsys',
        'ojvmsys',
        'olapsys',
        'orddata',
        'ordsys',
        'outln',
        'rdsadmin',
        'sys',
        'sysaux',
        'sysman',
        'system',
        'tsmsys',
        'wmsys',
        'xdb',
    ]

    table_properties = []

    definitions_sql = ORACLE_DEFINITIONS_SQL

    indexes_sql = ORACLE_INDEXES_SQL

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
        return ConnectionFactory

    @property
    def dictcursor(self):
        return None

    @property
    def cursor_kwargs(self):
        return {}

    @property
    def assertion_query(self):
        return "SELECT 1 as assertion FROM DBA_OBJECTS WHERE ROWNUM = 1"

    @property
    def operational_error(self):
        return cx_Oracle.DatabaseError

    def get_db_version(self):
        result = self.get_first(
            "SELECT banner FROM v$version WHERE banner LIKE 'Oracle%'"
        )
        if len(result):
            return result['banner']
        return None

    def get_tables_and_views_sql(self, excluded_schemas):
        """Generate SQL statement for getting tables and views.
        """
        positions = [
            ':%s' % str(i + 1)
            for i in range(len(excluded_schemas))
        ]
        return self.definitions_sql.format(excluded=', '.join(positions))

    def get_indexes_sql(self, excluded_schemas):
        """Generate SQL statement for getting indexes and constraints.
        """
        positions = [
            ':%s' % str(i + 1)
            for i in range(len(excluded_schemas))
        ]
        return self.indexes_sql.format(excluded=', '.join(positions))
