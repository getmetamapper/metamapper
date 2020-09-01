# -*- coding: utf-8 -*-
import boto3
import botocore.exceptions as exceptions

import app.inspector.engines.interface as interface


class AwsGlueInspector(interface.AmazonInspectorMixin):
    """Access Athena database metadata via AWS API.
    """
    aws_client_type = 'glue'

    @classmethod
    def has_indexes(self):
        """bool: BigQuery does not have indexes, so we default this to False.
        """
        return False

    @property
    def version(self):
        """str: The version of the BigQuery module that we're working with.
        """
        return boto3.__version__

    def verify_connection(self):
        """bool: Verify the ability to connect to the datastore.
        """
        try:
            self._ping()
        except (exceptions.ClientError, exceptions.NoCredentialsError, exceptions.ParamValidationError):
            return False
        return True

    def get_tables_and_views(self, *args, **kwargs):
        """generator: Retrieve the full list of table definitions for the provided datastore.
        """
        for dataset in self._list_datasets():
            for table in self._list_table_metadata(dataset['Name']):
                yield self._get_table_as_dict(
                    dataset['Name'],
                    table,
                )

    def get_indexes(self, *args, **kwargs):
        """list: Retrieve indexes from the database.
        """
        return []

    def _ping(self):
        """If this fails, we know we cannot connect.
        """
        self.client.get_databases(CatalogId=self.database)

    def _list_datasets(self, **extras):
        """List the datasets that this BigQuery service account has access to.
        """
        paginator = self.client.get_paginator('get_databases')

        for page in paginator.paginate(CatalogId=self.database, **extras):
            yield from page['DatabaseList']

    def _list_table_metadata(self, schema_name):
        """List the tables associated with the provided dataset ident.
        """
        paginator = self.client.get_paginator('get_tables')

        for page in paginator.paginate(CatalogId=self.database, DatabaseName=schema_name):
            yield from page['TableList']

    def _get_table_as_dict(self, schema_name, table):
        """Retrieve the table based on the provided reference. Format the table
        into the standard Metamapper inspector response.
        """
        full_table_id = '.'.join([self.database, schema_name, table['Name']])
        partition_col = [p['Name'] for p in table['PartitionKeys']]

        return {
            'schema_object_id': self._to_oid(self.database, schema_name),
            'table_schema': schema_name,
            'table_object_id': self._to_oid(full_table_id),
            'table_name': table['Name'],
            'table_type': table['TableType'],
            'properties': {},
            'columns': [
                {
                    'column_object_id': self._to_oid(full_table_id, column['Name']),
                    'column_name': column['Name'],
                    'ordinal_position': position,
                    'data_type': column['Type'].lower(),
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': column['Name'] in partition_col,
                    'default_value': "",
                }
                for position, column in enumerate(table['StorageDescriptor']['Columns'] + table['PartitionKeys'], 1)
            ],
        }
