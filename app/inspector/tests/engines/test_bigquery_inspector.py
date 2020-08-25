# -*- coding: utf-8 -*-
import types
import unittest
import unittest.mock as mock

import app.inspector.engines.bigquery_inspector as engine

from google.auth.exceptions import GoogleAuthError


class BigQueryInspectorTests(unittest.TestCase):
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
            'database': 'acme',
            'extras': {
                'credentials': {},
            }
        }
        self.engine = engine.BigQueryInspector(**self.connection)

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert not engine.BigQueryInspector.has_indexes()

    def test_get_indexes(self):
        """It should return an empty list.
        """
        assert not len(self.engine.get_indexes())

    def test_to_oid(self):
        """It should create a consistent object ident from the provided items.
        """
        test_cases = [
            (['public', 'accounts'], '35b988b5d5565f2c97d05172af404829'),
            (['public', 'account'], '94b4b3b08a0e6881f80d7b17b1ec3121'),
            (['bigquery-public-data', 'austin_311', 'people'], '578bb4d8ac036612e38c76ee334d2b95'),
            (['bigquery-public-data', 'austin_311', 'persons'], '65c4a4056633d86a0037b3e461c1d587'),
        ]

        for input_items, output in test_cases:
            self.assertEqual(self.engine._to_oid(*input_items), output)

    @mock.patch.object(engine.BigQueryInspector, '_list_datasets')
    def test_verify_connection_true(self, mock_list_datasets):
        """It should return True when we can hit the API properly.
        """
        mock_list_datasets._list_datasets.return_value = []
        self.assertTrue(self.engine.verify_connection())

    @mock.patch.object(engine.BigQueryInspector, '_list_datasets')
    def test_verify_connection_false(self, mock_list_datasets):
        """It should return false when a GoogleAuthError is raised.
        """
        mock_list_datasets.side_effect = GoogleAuthError('Bad credentials.')

        self.assertFalse(self.engine.verify_connection())

    @mock.patch.object(engine.BigQueryInspector, '_list_datasets')
    @mock.patch.object(engine.BigQueryInspector, '_list_tables')
    @mock.patch.object(engine.BigQueryInspector, '_get_table')
    def test_get_tables_and_views(self, mock_get_table, mock_list_tables, mock_list_datasets):
        """It should return the expected definitions.
        """
        mock_list_datasets.return_value = [
            mock.MagicMock(table_id='app%s' % str(i).zfill(3))
            for i in range(3)
        ]

        mock_list_tables.return_value = [
            mock.MagicMock(table_id='table%s' % str(i).zfill(3))
            for i in range(10)
        ]

        records = self.engine.get_tables_and_views()

        self.assertIsInstance(records, types.GeneratorType)
        self.assertEqual(len(list(records)), len(mock_list_tables.return_value) * len(mock_list_datasets.return_value))

    @mock.patch.object(engine.BigQueryInspector, '_list_datasets')
    @mock.patch.object(engine.BigQueryInspector, '_list_tables')
    def test_get_tables_and_views_empty(self, mock_list_tables, mock_list_datasets):
        """It should return an empty list.
        """
        mock_list_datasets.return_value = [
            mock.MagicMock(dataset_id='one'),
            mock.MagicMock(dataset_id='two'),
            mock.MagicMock(dataset_id='three'),
        ]

        mock_list_tables.return_value = []

        records = self.engine.get_tables_and_views()

        self.assertIsInstance(records, types.GeneratorType)
        self.assertEqual(list(records), [])

    @mock.patch.object(engine.BigQueryInspector, '_get_table')
    def test_get_table(self, mock_get_table):
        """It deserializes the table correctly.
        """
        schema = []

        for i in range(4):
            col = mock.MagicMock(
                is_nullable=False,
                field_type='string' if i % 2 == 0 else 'bigint',
            )
            col.name = 'name_%s' % str(i).zfill(3)
            schema.append(col)

        mock_get_table_attrs = {
            'project': 'production',
            'dataset_id': 'app',
            'table_id': 'accounts',
            'full_table_id': 'production.app.accounts',
            'num_rows': 1231,
            'table_type': 'VIEW',
            'schema': schema,
        }

        mock_get_table.return_value = mock.MagicMock(**mock_get_table_attrs)

        record = self.engine._get_table_as_dict('nothing')

        self.assertEqual(record, {
            'schema_object_id': '39c6eb83e42d666a584c70d3168223f9',
            'table_schema': 'app',
            'table_object_id': 'af0d2d8fedc475b8dc8ef7fb2cd12804',
            'table_name': 'accounts',
            'table_type': 'VIEW',
            'properties': {
                'num_rows': 1231
            },
            'columns': [
                {
                    'column_object_id': 'd99ac599f4a51e993edb1864f335636c',
                    'column_name': 'name_000',
                    'ordinal_position': 1,
                    'data_type': 'string',
                    'max_length': None,
                    'numeric_scale': None,
                    'is_nullable': False,
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
                    'is_nullable': False,
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
                    'is_nullable': False,
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
                    'is_nullable': False,
                    'is_primary': False,
                    'default_value': '',
                }
              ]
            })
