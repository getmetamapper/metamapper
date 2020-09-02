# -*- coding: utf-8 -*-
import app.inspector.engines.interface as interface

from app.definitions.models import Datastore

from app.inspector.engines.azure_inspector import AzureInspector  # noqa: F401
from app.inspector.engines.postgresql_inspector import PostgresqlInspector
from app.inspector.engines.mysql_inspector import MySQLInspector
from app.inspector.engines.sqlserver_inspector import SQLServerInspector


HIVE_METASTORE_DEFINITIONS_QUERY = """
SELECT source.* FROM
(
    SELECT
        d.NAME as table_schema,
        d.DB_ID as schema_object_id,
        t.TBL_NAME as table_name,
        t.TBL_ID as table_object_id,
        t.TBL_TYPE as table_type,
        CONCAT(t.TBL_ID, '/', p.PKEY_NAME) as column_object_id,
        p.PKEY_NAME as column_name,
        p.PKEY_COMMENT as column_description,
        p.INTEGER_IDX as ordinal_position,
        p.PKEY_TYPE as data_type,
        0 as is_nullable,
        1 as is_primary,
        '' as default_value
    FROM TBLS t
    JOIN DBS d ON t.DB_ID = d.DB_ID
    JOIN PARTITION_KEYS p ON t.TBL_ID = p.TBL_ID
    LEFT JOIN TABLE_PARAMS tp ON (t.TBL_ID = tp.TBL_ID AND tp.PARAM_KEY='comment')
    UNION
    SELECT
            d.NAME as table_schema,
            d.DB_ID as schema_object_id,
            t.TBL_NAME as table_name,
            t.TBL_ID as table_object_id,
            t.TBL_TYPE as table_type,
            CONCAT(t.TBL_ID, '/', c.COLUMN_NAME) as column_object_id,
            c.COLUMN_NAME as column_name,
            c.COMMENT as column_description,
            c.INTEGER_IDX as ordinal_position,
            c.TYPE_NAME as data_type,
            0 as is_nullable,
            0 as is_primary,
            '' as default_value
    FROM TBLS t
    JOIN DBS d ON t.DB_ID = d.DB_ID
    JOIN SDS s ON t.SD_ID = s.SD_ID
    JOIN COLUMNS_V2 c ON s.CD_ID = c.CD_ID
    LEFT JOIN TABLE_PARAMS tp ON (t.TBL_ID = tp.TBL_ID AND tp.PARAM_KEY='comment')
) source
ORDER by table_schema, table_name, ordinal_position
"""


HIVE_METASTORE_VERSION_QUERY = """
SELECT SCHEMA_VERSION FROM VERSION
"""


# The default Hive upgrade migrations create Postgres tables in quotes. This is done to
# force them uppercase. If we start seeing users with downcased tables, we can make the query
# routing process a bit more intelligent.
HIVE_METASTORE_DEFINITIONS_QUERY_WITH_QUOTES = """
SELECT source.* FROM
(
    SELECT
        d."NAME" as table_schema,
        d."DB_ID" as schema_object_id,
        t."TBL_NAME" as table_name,
        t."TBL_ID" as table_object_id,
        t."TBL_TYPE" as table_type,
        MD5(CONCAT(t."TBL_ID", '/', p."PKEY_NAME")) as column_object_id,
        p."PKEY_NAME" as column_name,
        p."PKEY_COMMENT" as column_description,
        p."INTEGER_IDX" as ordinal_position,
        p."PKEY_TYPE" as data_type,
        0 as is_nullable,
        1 as is_primary,
        '' as default_value
    FROM "TBLS" t
    JOIN "DBS" d ON t."DB_ID" = d."DB_ID"
    JOIN "PARTITION_KEYS" p ON t."TBL_ID" = p."TBL_ID"
    LEFT JOIN "TABLE_PARAMS" tp ON (t."TBL_ID" = tp."TBL_ID" AND tp."PARAM_KEY"='comment')
    UNION
    SELECT
            d."NAME" as table_schema,
            d."DB_ID" as schema_object_id,
            t."TBL_NAME" as table_name,
            t."TBL_ID" as table_object_id,
            t."TBL_TYPE" as table_type,
            MD5(CONCAT(t."TBL_ID", '/', c."COLUMN_NAME")) as column_object_id,
            c."COLUMN_NAME" as column_name,
            c."COMMENT" as column_description,
            c."INTEGER_IDX" as ordinal_position,
            c."TYPE_NAME" as data_type,
            0 as is_nullable,
            0 as is_primary,
            '' as default_value
    FROM "TBLS" t
    JOIN "DBS" d ON t."DB_ID" = d."DB_ID"
    JOIN "SDS" s ON t."SD_ID" = s."SD_ID"
    JOIN "COLUMNS_V2" c ON s."CD_ID" = c."CD_ID"
    LEFT JOIN "TABLE_PARAMS" tp ON (t."TBL_ID" = tp."TBL_ID" AND tp."PARAM_KEY"='comment')
) source
ORDER by table_schema, table_name, ordinal_position
"""


HIVE_METASTORE_VERSION_QUERY_WITH_QUOTES = """
SELECT "SCHEMA_VERSION" FROM "VERSION"
"""


supported_external_metastores = {
    Datastore.MYSQL: MySQLInspector,
    Datastore.POSTGRESQL: PostgresqlInspector,
    Datastore.SQLSERVER: SQLServerInspector,
}


supported_external_metastores_definitions_sql = {
    Datastore.MYSQL: HIVE_METASTORE_DEFINITIONS_QUERY,
    Datastore.POSTGRESQL: HIVE_METASTORE_DEFINITIONS_QUERY_WITH_QUOTES,
    Datastore.SQLSERVER: HIVE_METASTORE_DEFINITIONS_QUERY,
}

supported_external_metastores_version_sql = {
    Datastore.MYSQL: HIVE_METASTORE_VERSION_QUERY,
    Datastore.POSTGRESQL: HIVE_METASTORE_VERSION_QUERY_WITH_QUOTES,
    Datastore.SQLSERVER: HIVE_METASTORE_VERSION_QUERY,
}


class HiveMetastoreInspector(interface.EngineInterface):
    """Access external Hive metastore via JDBC connection. Supports schema version >= 2.0.0 on every datastore.
    """
    sys_schemas = []

    table_properties = []

    def __init__(self, host, username, password, port, database, extras=None):
        self.extras = extras or {}
        self.inspector = supported_external_metastores[self.dialect](
            host,
            username,
            password,
            port,
            database,
        )
        self.inspector.override_definitions_sql(supported_external_metastores_definitions_sql[self.dialect])
        self.inspector.override_sys_schema([])
        self._version = None

    @classmethod
    def has_indexes(self):
        return False

    @property
    def dialect(self):
        return self.extras.get('dialect')

    def get_db_version(self):
        result = self.inspector.get_first(supported_external_metastores_version_sql[self.dialect])
        if len(result):
            return result['SCHEMA_VERSION']
        return None

    def verify_connection(self):
        """bool: Verify the ability to connect to the datastore.
        """
        return self.inspector.verify_connection()

    def get_tables_and_views(self, *args, **kwargs):
        """generator: Retrieve the full list of table definitions for the provided datastore.
        """
        return self.inspector.get_tables_and_views(*args, **kwargs)

    def get_indexes(self, *args, **kwargs):
        """list: Retrieve indexes from the database.
        """
        return []
