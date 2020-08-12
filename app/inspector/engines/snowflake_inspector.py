# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

import snowflake.connector


SNOWFLAKE_DEFINITIONS_QUERY = """
SELECT
      LOWER(c.table_schema) AS "table_schema",
      c.table_schema_id AS "schema_object_id",
      LOWER(c.table_name) AS "table_name",
      c.table_id AS "table_object_id",
      COALESCE(LOWER(t.table_type), 'external table') AS "table_type",
      c.column_id AS "column_object_id",
      LOWER(c.column_name) as "column_name",
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


class SnowflakeInspector(interface.EngineInterface):
    """Access Snowflake database metadata.
    """
    sys_schemas = [
        'information_schema',
        'account_usage',
    ]

    table_properties = []

    definitions_sql = SNOWFLAKE_DEFINITIONS_QUERY

    connect_timeout_attr = 'login_timeout'

    @classmethod
    def has_indexes(self):
        return False

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

    def get_tables_and_views_sql(self, excluded_schemas):
        """Generate SQL statement for getting tables and views.
        """
        return self.definitions_sql.format(
            database=self.database.upper(),
            excluded=', '.join(['%s'] * len(excluded_schemas))
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
