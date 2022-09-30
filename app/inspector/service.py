# -*- coding: utf-8 -*-
import sshtunnel
import paramiko

from functools import wraps
from io import StringIO

from app.definitions.models import Datastore

# Ordering of import here matters. If we load Snowflake after
# Hive, for example, the lib dependencies cause a segmentation fault on Linux.
from app.inspector.engines import bigquery_inspector
from app.inspector.engines import redshift_inspector
from app.inspector.engines import snowflake_inspector

from app.inspector.engines import aws_athena_inspector
from app.inspector.engines import aws_glue_inspector
from app.inspector.engines import azure_inspector
from app.inspector.engines import hive_metastore_inspector
from app.inspector.engines import mysql_inspector
from app.inspector.engines import oracle_inspector
from app.inspector.engines import postgresql_inspector
from app.inspector.engines import sqlserver_inspector


engines = {
    Datastore.ATHENA: aws_athena_inspector.AwsAthenaInspector,
    Datastore.AZURE_DWH: azure_inspector.AzureInspector,
    Datastore.AZURE_SQL: azure_inspector.AzureInspector,
    Datastore.BIGQUERY: bigquery_inspector.BigQueryInspector,
    Datastore.GLUE: aws_glue_inspector.AwsGlueInspector,
    Datastore.HIVE: hive_metastore_inspector.HiveMetastoreInspector,
    Datastore.MYSQL: mysql_inspector.MySQLInspector,
    Datastore.ORACLE: oracle_inspector.OracleInspector,
    Datastore.POSTGRESQL: postgresql_inspector.PostgresqlInspector,
    Datastore.REDSHIFT: redshift_inspector.RedshiftInspector,
    Datastore.SNOWFLAKE: snowflake_inspector.SnowflakeInspector,
    Datastore.SQLSERVER: sqlserver_inspector.SQLServerInspector,
}


def with_ssh_tunnel():
    """Create an SSH tunnel when applicable.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(datastore, *args, **kwargs):
            """Execution function.
            """
            if not datastore.ssh_enabled:
                return func(datastore, *args, **kwargs)
            ssh_pkey = datastore.workspace.ssh_private_key
            with sshtunnel.SSHTunnelForwarder(
                (datastore.ssh_host, datastore.ssh_port),
                ssh_username=datastore.ssh_user,
                ssh_pkey=paramiko.RSAKey.from_private_key(StringIO(ssh_pkey)),
                remote_bind_address=(datastore.host, datastore.port),
            ) as server:
                return func(
                    datastore,
                    *args,
                    override_host=server.local_bind_host,
                    override_port=server.local_bind_port,
                    **kwargs)
        return wrapper
    return decorator


def construct_conn_dict(datastore, override_host=None, override_port=None):
    """Struct for Datastore connection parameters.
    """
    host = override_host or datastore.host
    port = override_port or datastore.port
    return {
        'host': host,
        'username': datastore.username,
        'password': datastore.password,
        'port': port,
        'database': datastore.database,
        'extras': datastore.extras,
    }


def get_inspector_class(engine):
    """Helper function to get the inspector class.
    """
    return engines[engine]


def get_engine(datastore, override_host=None, override_port=None):
    """Helper function to instantiate the engine.
    """
    config = construct_conn_dict(
        datastore,
        override_host,
        override_port,
    )
    return get_inspector_class(datastore.engine)(**config)


@with_ssh_tunnel()
def version(datastore, override_host=None, override_port=None):
    """Retrieve the Datastore version as a string.
    """
    return get_engine(datastore, override_host, override_port).version


@with_ssh_tunnel()
def tables_and_views(datastore, override_host=None, override_port=None):
    """Retrieve table and view definitions associated with a Datastore.
    """
    return get_engine(datastore, override_host, override_port).get_tables_and_views()


@with_ssh_tunnel()
def indexes(datastore, override_host=None, override_port=None):
    """Retrieve indexes associated with a Datastore.
    """
    return get_engine(datastore, override_host, override_port).get_indexes()


@with_ssh_tunnel()
def query_history(datastore, start_date, end_date, override_host=None, override_port=None):
    """Retrieve query history associated with a Datastore.
    """
    return get_engine(datastore, override_host, override_port).get_query_history(start_date, end_date)


@with_ssh_tunnel()
def verify_connection(datastore, override_host=None, override_port=None):
    """Verify the ability to connect to the datastore.
    """
    return get_engine(datastore, override_host, override_port).verify_connection()


@with_ssh_tunnel()
def get_dataframe(datastore, sql, byte_limit=(1000000 * 100), record_limit=None, override_host=None, override_port=None):
    """Execute a query and return the results as a list of dicts.
    """
    return get_engine(datastore, override_host, override_port).get_dataframe(sql, byte_limit, record_limit)
