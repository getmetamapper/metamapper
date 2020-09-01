# -*- coding: utf-8 -*-
import types
import unittest
import unittest.mock as mock

import app.inspector.engines.aws_glue_inspector as engine
import botocore.exceptions as exceptions


class AwsGlueInspectorTests(unittest.TestCase):
    """Tests to ensure that the engine follows the subscribed interface.
    """
    def setUp(self):
        """Get ready for some tests...
        """
        self.connection = {
            'host': 'localhost',
            'username': 'admin',
            'password': '1234567890',
            'port': 3306,
            'database': 'production',
            'extras': {
                'role': 'meowmeowmeow',
                'region': 'us-west-2',
            }
        }
        self.engine = engine.AwsGlueInspector(**self.connection)

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert not engine.AwsGlueInspector.has_indexes()

    def test_get_indexes(self):
        """It should return an empty list.
        """
        assert not len(self.engine.get_indexes())

    def test_iam_role(self):
        """It should parse out the AWS IAM role.
        """
        self.assertEqual(self.engine.iam_role, 'meowmeowmeow')

    def test_region(self):
        """It should parse out the AWS region.
        """
        self.assertEqual(self.engine.region, 'us-west-2')

    @mock.patch.object(engine.AwsGlueInspector, '_ping')
    def test_verify_connection(self, mock_ping):
        """It should return True when we can hit the API properly.
        """
        mock_ping.return_value = [
            {
                'CatalogName': 'production',
            },
        ]

        self.assertTrue(self.engine.verify_connection())

    @mock.patch.object(engine.AwsGlueInspector, '_ping')
    def test_verify_connection_on_param_error(self, mock_ping):
        """It should return False when the catalog does not exist.
        """
        mock_ping.side_effect = exceptions.ParamValidationError(report=None)

        self.assertFalse(self.engine.verify_connection())

    @mock.patch.object(engine.AwsGlueInspector, '_ping')
    def test_verify_connection_on_creds_error(self, mock_ping):
        """It should return False when the catalog does not exist.
        """
        mock_ping.side_effect = exceptions.NoCredentialsError()

        self.assertFalse(self.engine.verify_connection())

    @mock.patch.object(engine.AwsGlueInspector, '_list_datasets')
    @mock.patch.object(engine.AwsGlueInspector, '_list_table_metadata')
    def test_get_tables_and_views(self, mock_list_tables, mock_list_datasets):
        """It should return the expected definitions.
        """
        mock_list_datasets.return_value = [
            {'Name': 'one'},
            {'Name': 'two'},
            {'Name': 'three'},
        ]

        mock_list_tables.return_value = [
            {'Name': 'table_1', 'TableType': 'VIEW', 'StorageDescriptor': {'Columns': []}, 'PartitionKeys': []},
            {'Name': 'table_2', 'TableType': 'VIEW', 'StorageDescriptor': {'Columns': []}, 'PartitionKeys': []},
            {'Name': 'table_3', 'TableType': 'VIEW', 'StorageDescriptor': {'Columns': []}, 'PartitionKeys': []},
            {'Name': 'table_4', 'TableType': 'VIEW', 'StorageDescriptor': {'Columns': []}, 'PartitionKeys': []},
        ]

        records = self.engine.get_tables_and_views()

        self.assertIsInstance(records, types.GeneratorType)
        self.assertIsInstance(records, types.GeneratorType)
        self.assertEqual(len(list(records)), len(mock_list_tables.return_value) * len(mock_list_datasets.return_value))

    @mock.patch.object(engine.AwsGlueInspector, '_list_datasets')
    @mock.patch.object(engine.AwsGlueInspector, '_list_table_metadata')
    def test_get_tables_and_views_empty(self, mock_list_tables, mock_list_datasets):
        """It should return an empty list.
        """
        mock_list_datasets.return_value = [
            {'Name': 'one'},
            {'Name': 'two'},
            {'Name': 'three'},
        ]

        mock_list_tables.return_value = []

        records = self.engine.get_tables_and_views()

        self.assertIsInstance(records, types.GeneratorType)
        self.assertEqual(list(records), [])

    def test_get_table(self):
        """It deserializes the table correctly.
        """
        schema = []

        for i in range(4):
            col = {
                'Name': 'name_%s' % str(i).zfill(3),
                'Type': 'string' if i % 2 == 0 else 'bigint',
            }
            schema.append(col)

        table_metadata = {
            'Name': 'accounts',
            'TableType': 'VIEW',
            'StorageDescriptor': {
                'Columns': schema,
            },
            'PartitionKeys': [
                {
                    'Name': 'name_004',
                    'Type': 'bigint',
                }
            ]
        }

        record = self.engine._get_table_as_dict('app', table_metadata)

        self.assertEqual(record, {
            'schema_object_id': '39c6eb83e42d666a584c70d3168223f9',
            'table_schema': 'app',
            'table_object_id': 'af0d2d8fedc475b8dc8ef7fb2cd12804',
            'table_name': 'accounts',
            'table_type': 'VIEW',
            'properties': {},
            'columns': [
                {
                    'column_object_id': 'd99ac599f4a51e993edb1864f335636c',
                    'column_name': 'name_000',
                    'ordinal_position': 1,
                    'data_type': 'string',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': False,
                    'default_value': '',
                },
                {
                    'column_object_id': '428daceac1f67db20a4f9d1a33ef4bf0',
                    'column_name': 'name_001',
                    'ordinal_position': 2,
                    'data_type': 'bigint',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': False,
                    'default_value': '',
                },
                {
                    'column_object_id': 'f57bb57d15d32fd04800a8168ee29ce4',
                    'column_name': 'name_002',
                    'ordinal_position': 3,
                    'data_type': 'string',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': False,
                    'default_value': '',
                },
                {
                    'column_object_id': '210f5f939018a68f8811fa837c8af8bd',
                    'column_name': 'name_003',
                    'ordinal_position': 4,
                    'data_type': 'bigint',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': False,
                    'default_value': '',
                },
                {
                    'column_object_id': '6a0929a579a5c2d50004e6ab2ed65d69',
                    'column_name': 'name_004',
                    'ordinal_position': 5,
                    'data_type': 'bigint',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': True,
                    'is_primary': True,
                    'default_value': '',
                }
            ]
        })
