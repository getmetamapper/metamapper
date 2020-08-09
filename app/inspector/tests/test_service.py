# -*- coding: utf-8 -*-
import collections
import types
import unittest
import unittest.mock as mock

import app.inspector.engines.postgresql_inspector as interface
import app.inspector.service as service

import app.inspector.tests.fixtures.indexes as indexes
import app.inspector.tests.fixtures.tables_and_views as tables_and_views


Datastore = collections.namedtuple("Datastore", [
    "engine",
    "username",
    "password",
    "host",
    "port",
    "database",
    "ssh_enabled",
])


class InspectorServiceTests(unittest.TestCase):
    """Tests with mocked data for service functions.
    """
    def setUp(self):
        """Get ready for some tests...
        """
        self.connection = {
            'engine': 'postgresql',
            'username': None,
            'password': None,
            'host': None,
            'port': None,
            'database': None,
            'ssh_enabled': False,
        }

        self.datastore = Datastore(**self.connection)

    @mock.patch.object(interface.PostgresqlInspector, 'get_db_version', return_value='10.0.0')
    def test_version(self, get_db_version):
        """It should return the current version of the datastore.
        """
        self.assertEqual(
            service.version(self.datastore),
            '10.0.0',
        )

    @mock.patch.object(interface.PostgresqlInspector, 'get_first', return_value={})
    def test_version_when_returns_none(self, get_db_version):
        """It should return NoneType if empty.
        """
        self.assertEqual(
            service.version(self.datastore),
            None
        )

    @mock.patch.object(interface.PostgresqlInspector, 'get_first', return_value={'assertion': 1})
    def test_verify_connection_when_true_lowercase(self, get_db_version):
        """It should return TRUE if the assertion is lowercase.
        """
        self.assertEqual(
            service.verify_connection(self.datastore),
            True,
        )

    @mock.patch.object(interface.PostgresqlInspector, 'get_first', return_value={'ASSERTION': 1})
    def test_verify_connection_when_true_uppercase(self, get_first):
        """It should return TRUE if the assertion is uppercase.
        """
        self.assertEqual(
            service.verify_connection(self.datastore),
            True,
        )

    @mock.patch.object(interface.PostgresqlInspector, 'get_first', return_value={})
    def test_verify_connection_when_false(self, get_first):
        """It should return FALSE if nothing is returned.
        """
        self.assertEqual(
            service.verify_connection(self.datastore),
            False,
        )

    @mock.patch.object(interface.PostgresqlInspector, 'get_records', return_value=indexes.RAW)
    def test_indexes(self, get_records):
        """It should parse the index query output properly.
        """
        self.assertEqual(service.indexes(self.datastore), indexes.PROCESSED)

    @mock.patch.object(interface.PostgresqlInspector, 'get_records_batched', return_value=tables_and_views.RAW)
    def test_tables_and_views(self, get_records):
        """It should parse the index query output properly.
        """
        records = service.tables_and_views(self.datastore)
        self.assertIsInstance(records, types.GeneratorType)
        self.assertEqual(list(records), tables_and_views.PROCESSED)
