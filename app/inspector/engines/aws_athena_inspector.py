# -*- coding: utf-8 -*-
import boto3
import botocore.exceptions as exceptions

import app.inspector.dbapi2.aws_athena as aws_athena
import app.inspector.engines.interface as interface


class AwsAthenaInspector(interface.AmazonInspectorInterface):
    """Access Athena database metadata via AWS API.
    """
    aws_client_type = 'athena'

    @property
    def version(self):
        """str: The version of the Athena module that we're working with.
        """
        return boto3.__version__

    @property
    def connect_kwargs(self):
        _kwargs = {
            'role_arn': self.iam_role,
            'region_name': self.region,
            'work_group': self.work_group,
            'catalog_name': self.database,
            'timeout': 120,
        }
        return _kwargs

    @property
    def operational_error(self):
        return exceptions.ClientError

    @property
    def catchable_errors(self):
        return (
            self.operational_error,
            aws_athena.DatabaseError,
            exceptions.NoCredentialsError,
            exceptions.ParamValidationError,
        )

    def get_last_commit_time_for_table(self, *args, **kwargs):
        """Retrieve the last time a table was modified.
        """
        return None

    def verify_connection(self):
        """bool: Verify the ability to connect to the datastore.
        """
        try:
            for r in self._list_data_catalogs():
                if r['CatalogName'] == self.database:
                    return True
        except (exceptions.ClientError, exceptions.NoCredentialsError, exceptions.ParamValidationError):
            return False
        return False

    def get_tables_and_views(self, *args, **kwargs):
        """generator: Retrieve the full list of table definitions for the provided datastore.
        """
        for dataset in self._list_datasets():
            for table_metadata in self._list_table_metadata(dataset['Name']):
                yield self._get_table_as_dict(
                    dataset['Name'],
                    table_metadata,
                )

    def _list_data_catalogs(self):
        """List the available data catalogs via API
        """
        return self.client.list_data_catalogs()['DataCatalogsSummary']

    def _list_datasets(self, **extras):
        """List the datasets that this Athena service account has access to.
        """
        paginator = self.client.get_paginator('list_databases')

        for page in paginator.paginate(CatalogName=self.database, **extras):
            yield from page['DatabaseList']

    def _list_table_metadata(self, schema_name):
        """List the tables associated with the provided dataset ident.
        """
        paginator = self.client.get_paginator('list_table_metadata')

        for page in paginator.paginate(CatalogName=self.database, DatabaseName=schema_name):
            yield from page['TableMetadataList']

    def _get_data_type(self, data_type):
        if data_type[:6] == 'struct':
            return 'struct'
        return data_type

    def _get_table_as_dict(self, schema_name, table):
        """Retrieve the table based on the provided reference. Format the table into the standard inspector response.
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
                    'column_description': column.get('Comment'),
                    'ordinal_position': position,
                    'data_type': self._get_data_type(column['Type'].lower()),
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': column['Name'] in partition_col,
                    'default_value': "",
                }
                for position, column in enumerate(table['Columns'] + table['PartitionKeys'], 1)
            ],
        }
