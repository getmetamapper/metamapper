# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import snowflake.connector


SNOWFLAKE_DEFINITIONS_SQL = """
SELECT
      LOWER(c.table_schema) AS "table_schema",
      c.table_schema_id AS "schema_object_id",
      LOWER(c.table_name) AS "table_name",
      c.table_id AS "table_object_id",
      COALESCE(LOWER(t.table_type), 'external table') AS "table_type",
      c.column_id AS "column_object_id",
      LOWER(c.column_name) as "column_name",
      c.comment AS "column_description",
      c.ordinal_position as "ordinal_position",
      LOWER(c.data_type) as "data_type",
      CASE WHEN c.character_maximum_length IS NOT NULL
           THEN c.character_maximum_length
           ELSE c.numeric_precision END AS "max_length",
      c.numeric_scale as "numeric_scale",
      CASE WHEN UPPER(c.is_nullable) = 'YES'
           THEN TRUE
           ELSE FALSE END AS "is_nullable",
      FALSE AS "is_primary",
      COALESCE(ic.column_default, '') AS "default_value"
 FROM snowflake.account_usage.columns c
 JOIN snowflake.account_usage.tables t
   ON c.table_schema = t.table_schema
  AND c.table_name = t.table_name
  AND c.table_catalog = t.table_catalog
 LEFT JOIN information_schema.columns ic
   ON c.table_schema = ic.table_schema
  AND c.table_name = ic.table_name
  AND c.column_name = ic.column_name
  AND c.table_catalog = ic.table_catalog
WHERE UPPER(t.table_catalog) = '{database}'
  AND LOWER(c.table_schema) NOT IN ({excluded})
  AND (c.deleted IS NULL AND t.deleted IS NULL)
ORDER BY LOWER(c.table_schema), LOWER(c.table_name), c.ordinal_position
"""

SNOWFLAKE_QUERY_HISTORY_SQL = """
WITH queries AS (
  SELECT
    qh.query_text,
    DATE(qh.end_time) as execution_date,
    LOWER(qh.database_name) as db_name,
    COALESCE(LOWER(qh.schema_name), 'public') as db_schema,
    LOWER(qh.user_name) as db_user
  FROM snowflake.account_usage.query_history qh
 WHERE qh.EXECUTION_STATUS = 'SUCCESS'
   AND qh.query_type = 'SELECT'
   AND UPPER(qh.database_name) = '{database}'
   AND DATE(qh.end_time) >= '{start_date}'
   AND DATE(qh.end_time) <= '{end_date}'
   AND qh.query_text NOT ILIKE 'CALL%'
)

SELECT
    query_text,
    execution_date,
    db_schema,
    db_name,
    db_user,
    COUNT(1) as "query_count"
 FROM queries
GROUP BY
    query_text,
    execution_date,
    db_schema,
    db_name,
    db_user
"""


class SnowflakeInspector(interface.EngineInterface):
    """Access Snowflake database metadata.
    """
    sys_schemas = [
        'information_schema',
        'account_usage',
    ]

    table_properties = []

    definitions_sql = SNOWFLAKE_DEFINITIONS_SQL

    query_history_sql = SNOWFLAKE_QUERY_HISTORY_SQL

    connect_timeout_attr = 'login_timeout'

    @classmethod
    def has_indexes(self):
        return False

    @classmethod
    def has_query_history(self):
        return True

    @property
    def connect_kwargs(self):
        return {
            'account': self.host,
            'database': self.database,
            'password': self.password,
            'user': self.username,
            'login_timeout': self.connect_timeout_value,
        }

    @property
    def connector(self):
        return snowflake.connector

    @property
    def dictcursor(self):
        return snowflake.connector.DictCursor

    @property
    def cursor_kwargs(self):
        return {'cursor_class': self.dictcursor}

    def get_db_version(self):
        result = self.get_first("SELECT CURRENT_VERSION() as VERSION")
        if len(result):
            return result['VERSION']
        return None

    def get_last_commit_time_for_table(self, table_schema, table_name):
        """Retrieve the last time a table was modified.
        """
        try:
            result = self.get_first(
                sql="SELECT TO_TIMESTAMP_NTZ(SYSTEM$LAST_CHANGE_COMMIT_TIME(%s) / 1000) as TS",
                parameters=('.'.join([table_schema, table_name]),)
            )
        except self.connector.DatabaseError:
            return None
        if len(result):
            return result['TS']
        return None

    def get_tables_and_views_sql(self, excluded_schemas):
        """Generate SQL statement for getting tables and views.
        """
        return self.definitions_sql.format(
            database=self.database.upper(),
            excluded=', '.join(['%s'] * len(excluded_schemas))
        )

    def get_query_history_sql(self, start_date, end_date):
        """Generate SQL statement for getting query history.
        """
        return self.query_history_sql.format(
            database=self.database.upper(),
            start_date=start_date,
            end_date=end_date,
        )

    def get_indexes(self, *args, **kwargs):
        """Retrieve indexes from the database.
        """
        return []

    def get_cursor(self, connection):
        """Wrapper function around Connection.cursor so we can run pre-SQL if needed.
        """
        cursor = connection.cursor(**self.cursor_kwargs)
        cursor.execute("USE DATABASE {}".format(self.database))
        return cursor
