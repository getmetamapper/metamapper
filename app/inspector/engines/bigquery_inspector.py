# -*- coding: utf-8 -*-
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import md5

from google.auth.exceptions import GoogleAuthError
from google.cloud import bigquery
from google.cloud.bigquery.dbapi.exceptions import DatabaseError, OperationalError
from google.oauth2 import service_account


class BigQueryInspector(object):
    """Access BigQuery database metadata via Google API.
    """
    scopes = ['https://www.googleapis.com/auth/cloud-platform']

    def __init__(self, host, username, password, port, database, extras=None):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.database = database
        self.extras = extras or {}
        self._version = None
        self._client = None
        self.threads = 5

    @property
    def operational_error(self):
        return OperationalError

    @property
    def catchable_errors(self):
        return (self.operational_error, DatabaseError, GoogleAuthError)

    @property
    def project(self):
        return self.database

    @property
    def account_info(self):
        return self.extras.get('credentials', {})

    @classmethod
    def has_checks(self):
        return True

    @classmethod
    def has_indexes(self):
        return False

    @classmethod
    def has_partitions(self):
        return False

    @classmethod
    def has_usage(self):
        return False

    @property
    def version(self):
        """str: The version of the BigQuery module that we're working with.
        """
        return bigquery.__version__

    @property
    def client(self):
        """bigquery.Client: Cached method of grabbing a BigQuery client. We do this to avoid credential errors during
        the __init__ lifecycle, but prior to making any API calls.
        """
        if not self._client:
            try:
                credentials = service_account.Credentials.from_service_account_info(
                    self.account_info,
                    scopes=self.scopes,
                )
            except ValueError:
                raise GoogleAuthError('Provided service account credentials are invalid.')
            self._client = bigquery.Client(credentials=credentials, project=self.project)
        return self._client

    def get_last_commit_time_for_table(self, *args, **kwargs):
        """Retrieve the last time a table was modified.
        """
        return None

    def verify_connection(self):
        """bool: Verify the ability to connect to the datastore.
        """
        try:
            list(self._list_datasets(max_results=1))
        except GoogleAuthError:
            return False
        return True

    def get_tables_and_views(self, *args, **kwargs):
        """generator: Retrieve the full list of table definitions for the provided datastore.
        """
        for dataset in self._list_datasets(as_reference=True):
            threads = []

            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                for tbl in self._list_tables(dataset.dataset_id):
                    threads.append(
                        executor.submit(self._get_table_as_dict, dataset.table(tbl.table_id))
                    )

                for task in as_completed(threads):
                    yield task.result()

    def get_indexes(self, *args, **kwargs):
        """list: Retrieve indexes from the database.
        """
        return []

    def _to_oid(self, *items):
        """str: We create a consistent hash of items to create a `pseudo` object identifier.
        """
        return md5(''.join(map(str, items)).encode('utf-8')).hexdigest()

    def _list_datasets(self, as_reference=False, **extras):
        """List the datasets that this BigQuery service account has access to.
        """
        datasets = self.client.list_datasets(project=self.project, **extras)

        if as_reference:
            datasets = [
                bigquery.DatasetReference(self.project, dataset.dataset_id)
                for dataset in datasets
            ]

        return datasets

    def _list_tables(self, dataset_id):
        """List the tables associated with the provided dataset ident.
        """
        return self.client.list_tables(dataset_id)

    def _get_table(self, table_reference):
        """Retrieve the table based on the provided reference.
        """
        return self.client.get_table(table_reference)

    def _get_table_as_dict(self, table_reference):
        """Format the table into the standard Metamapper inspector response.
        """
        table_object = self._get_table(table_reference)

        return {
            'schema_object_id': self._to_oid(table_object.project, table_object.dataset_id),
            'table_schema': table_object.dataset_id,
            'table_object_id': self._to_oid(table_object.full_table_id),
            'table_name': table_object.table_id,
            'table_type': table_object.table_type,
            'properties': {
                'num_rows': table_object.num_rows,
            },
            'columns': [
                {
                    'column_object_id': self._to_oid(table_object.full_table_id, column.name),
                    'column_name': column.name,
                    'column_description': column.description,
                    'ordinal_position': position,
                    'data_type': column.field_type.lower(),
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': column.is_nullable,
                    'is_primary': False,
                    'default_value': "",
                }
                for position, column in enumerate(table_object.schema, 1)
            ],
        }
