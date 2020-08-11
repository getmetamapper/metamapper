# -*- coding: utf-8 -*-
import contextlib
import sys


class EngineInterface(object):
    """Default class for an Inspector engine.
    """
    sys_schemas = []

    table_properties = []

    definitions_sql = None

    indexes_sql = None

    connect_timeout_attr = None

    connect_timeout_value = 5

    records_per_batch = 1000

    def __init__(self, host, username, password, port, database):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.database = database
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
    def cursor_kwargs(self):
        return {'cursorclass': self.dictcursor}

    @property
    def assertion_query(self):
        return 'SELECT 1 as assertion'

    @property
    def operational_error(self):
        return self.connector.OperationalError

    @classmethod
    def has_indexes(self):
        raise NotImplementedError()

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
        except self.operational_error as e:
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
