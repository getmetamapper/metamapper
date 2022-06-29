# -*- coding: utf-8 -*-
import boto3
import contextlib
import pandas as pd
import numpy as np
import hashlib
import sys

from app.inspector.errors import OutOfMemoryError


class EngineInterface(object):
    """Default class for an Inspector engine.
    """
    sys_schemas = []

    table_properties = []

    definitions_sql = None

    query_history_sql = None

    indexes_sql = None

    connect_timeout_attr = None

    connect_timeout_value = 5

    records_per_batch = 1000

    def __init__(self, host, username, password, port, database, extras=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.database = database
        self.extras = extras or {}
        self._version = None

    @property
    def connector(self):
        raise NotImplementedError()

    @property
    def dictcursor(self):
        raise NotImplementedError()

    @property
    def connect_kwargs(self):
        _kwargs = {
            'host': self.host,
            'user': self.username,
            'password': self.password,
            'port': self.port,
            'database': self.database,
        }
        if self.connect_timeout_attr is not None:
            _kwargs[self.connect_timeout_attr] = self.connect_timeout_value
        return _kwargs

    @property
    def version(self):
        if not self._version:
            self._version = self.get_db_version()
        return self._version

    @property
    def last_updated_at(self):
        return None

    @property
    def cursor_kwargs(self):
        return {'cursorclass': self.dictcursor}

    @property
    def assertion_query(self):
        return 'SELECT 1 as assertion'

    @property
    def operational_error(self):
        return self.connector.OperationalError

    @property
    def programming_error(self):
        return self.connector.ProgrammingError

    @property
    def catchable_errors(self):
        return (self.operational_error, self.programming_error, OutOfMemoryError)

    @classmethod
    def has_checks(self):
        raise NotImplementedError()

    @classmethod
    def has_indexes(self):
        raise NotImplementedError()

    @classmethod
    def has_usage(self):
        raise NotImplementedError()

    def get_last_commit_time_for_table(self, *args, **kwargs):
        """Retrieve the last time a table was modified.
        """
        return None

    def get_db_version(self):
        """Retrieve the version of the provided datastore.
        """
        raise NotImplementedError()

    def parse_table_properties(self, data):
        """Helper function to transform metadata to properties format.
        """
        return {p: data.pop(p, None) for p in self.table_properties}

    def get_tables_and_views_sql(self, excluded_schemas):
        """Generate SQL statement for getting tables and views.
        """
        return self.definitions_sql.format(excluded=', '.join(['%s'] * len(excluded_schemas)))

    def get_indexes_sql(self, excluded_schemas):
        """Generate SQL statement for getting indexes and constraints.
        """
        return self.indexes_sql.format(excluded=', '.join(['%s'] * len(excluded_schemas)))

    def get_query_history_sql(self, start_date, end_date):
        """Generate SQL statement for getting query history.
        """
        return self.query_history_sql.format(start_date=start_date, end_date=end_date)

    def get_tables_and_views(self, *args, **kwargs):
        """Retrieve the full list of table definitions for the provided datastore.
        """
        querytxt = self.get_tables_and_views_sql(self.sys_schemas)
        response = {}

        last_source = None

        for number, record in enumerate(
            self.get_records_batched(querytxt, parameters=self.sys_schemas)
        ):
            record = self.lower_keys(record)
            source = "{table_schema}.{table_name}".format(**record)
            properties = self.parse_table_properties(record)

            schema_object_id = record.pop('schema_object_id')
            table_object_id = record.pop('table_object_id')
            table_schema = record.pop('table_schema')
            table_name = record.pop('table_name')
            table_type = record.pop('table_type')

            if source not in response:
                response[source] = {
                    'schema_object_id': schema_object_id,
                    'table_schema': table_schema,
                    'table_object_id': table_object_id,
                    'table_name': table_name,
                    'table_type': table_type,
                    'properties': properties,
                    'columns': [],
                }

            response[source]['columns'].append(record)

            if number > 0 and last_source != source:
                yield response.pop(last_source)

            last_source = source

        for source in response.keys():
            yield response[source]

    def get_indexes(self, *args, **kwargs):
        """Retrieve indexes from the database.
        """
        querytxt = self.get_indexes_sql(self.sys_schemas)
        response = {}

        for record in self.get_records(querytxt, parameters=self.sys_schemas):
            record = self.lower_keys(record)
            source = "{schema_name}.{table_name}.{index_name}".format(**record)

            column_name = record.pop('column_name')
            ordinal_position = record.pop('ordinal_position')

            if source not in response:
                response[source] = record
                response[source]['columns'] = []

            response[source]['columns'].append({
                'column_name': column_name,
                'ordinal_position': ordinal_position,
            })

        return list(response.values())

    def get_query_history(self, start_date, end_date, *args, **kwargs):
        """Retrieve past queries for the given date.
        """
        for record in self.get_records_batched(
            self.get_query_history_sql(start_date, end_date)
        ):
            yield self.lower_keys(record)

    @contextlib.contextmanager
    def execute_query(self, sql, parameters=None):
        if sys.version_info[0] < 3:
            sql = sql.encode('utf-8')

        with contextlib.closing(self.get_connection()) as conn:
            with contextlib.closing(self.get_cursor(conn)) as cursor:
                if parameters is not None:
                    cursor.execute(sql, tuple(parameters))
                else:
                    cursor.execute(sql)
                yield cursor

    def get_records_batched(self, sql, parameters=None):
        """Executes the sql and returns a set of records.
        """
        with self.execute_query(sql, parameters) as cursor:
            while True:
                done = True
                for r in cursor.fetchmany(self.records_per_batch):
                    done = False
                    yield r
                if done:
                    return

    def get_dataframe(self, sql, byte_limit=None, record_limit=None, parameters=None):
        """Executes the sql and returns a set of records.
        """
        data = []
        with self.execute_query(sql, parameters) as cursor:
            dataframe = pd.DataFrame(columns=[i[0] for i in cursor.description])
            while True:
                done = True
                for r in cursor.fetchmany(self.records_per_batch):
                    done = False
                    data.append(r)
                    if record_limit and len(data) >= record_limit:
                        break
                    if byte_limit and sys.getsizeof(data) >= byte_limit:
                        raise OutOfMemoryError()
                if done:
                    break
        dataframe = dataframe.append(data, ignore_index=True, sort=False)
        dataframe = dataframe.replace({np.nan: None})
        dataframe.columns = dataframe.columns.str.lower()
        return dataframe

    def get_records(self, sql, parameters=None):
        """Executes the sql and returns a set of records.
        """
        with self.execute_query(sql, parameters) as cursor:
            return cursor.fetchall()

    def get_first(self, sql, parameters=None):
        """Executes the sql and returns the first record.
        """
        with self.execute_query(sql, parameters) as cursor:
            return cursor.fetchone()

    def verify_connection(self):
        """Verify the ability to connect to the datastore.
        """
        try:
            result = self.get_first(self.assertion_query)
        except self.operational_error:
            return False
        if len(result):
            try:
                assertion = result['assertion']
            except KeyError:
                assertion = result['ASSERTION']
            return assertion == 1
        return False

    def get_connection(self):
        """Returns a connection object based on the connector property.
        """
        return self.connector.connect(**self.connect_kwargs)

    def get_cursor(self, connection):
        """Wrapper function around Connection.cursor so we can run pre-SQL if needed.
        """
        return connection.cursor(**self.cursor_kwargs)

    def lower_keys(self, r_dict):
        return {
            k.lower(): v for k, v in r_dict.items()
        }

    def override_definitions_sql(self, sql):
        self.definitions_sql = sql

    def override_sys_schema(self, schemas):
        self.sys_schemas = schemas


class AmazonInspectorMixin(object):
    """Adds some common funcitonality for inspectors that hit the Amazon API.
    """
    aws_client_type = None

    def __init__(self, host, username, password, port, database, extras=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.database = database
        self.extras = extras or {}
        self._client = None

    @property
    def client(self):
        if not self._client:
            sts = boto3.client('sts', region_name=self.region)

            assumed_role_object = sts.assume_role(
                RoleArn=self.iam_role,
                RoleSessionName=f'metamapper_{self.region}_{self.database}'
            )

            credentials = assumed_role_object['Credentials']

            self._client = boto3.client(
                self.aws_client_type,
                aws_access_key_id=credentials['AccessKeyId'],
                aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'],
                region_name=self.region,
            )
        return self._client

    @classmethod
    def has_checks(self):
        return False

    @classmethod
    def has_indexes(self):
        return False

    @classmethod
    def has_usage(self):
        return False

    @property
    def iam_role(self):
        return self.extras.get('role')

    @property
    def region(self):
        return self.extras.get('region')

    def _to_oid(self, *items):
        """str: We create a consistent hash of items to create a `pseudo` object identifier.
        """
        return hashlib.md5(''.join(map(str, items)).encode('utf-8')).hexdigest()
