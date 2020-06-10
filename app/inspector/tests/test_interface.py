# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

import app.definitions.models as models

import app.inspector.engines.interface as interface
import app.inspector.service as service


class InspectorInterfaceTests(unittest.TestCase):
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
        }

        self.engines = {}
        for name, engine in service.engines.items():
            self.engines[name] = engine(**self.connection)

    def test_all_engines_implemented(self):
        """We should have inspector engines for every allowed Datastore.
        """
        for dialect, name in models.Datastore.ENGINE_CHOICES:
            self.assertIn(
                dialect,
                service.engines,
                '%s engine has not been implemented.' % name,
            )

    def test_has_connector(self):
        """It should implement the connector property.
        """
        for name, engine in self.engines.items():
            try:
                engine.connector
            except AttributeError:
                self.assertFalse(
                    True,
                    '%s does not implement `connector` properly.' % name,
                )

    def test_connector_can_connect(self):
        """Every connector needs a `connect` function.
        """
        for name, engine in self.engines.items():
            assert callable(engine.connector.connect)

    def test_has_dictcursor(self):
        """It should implement the dictcursor property.
        """
        for name, engine in self.engines.items():
            try:
                engine.dictcursor
            except AttributeError:
                self.assertFalse(
                    True,
                    '%s does not implement `dictcursor` properly.' % name,
                )

    def test_has_indexes_class_method(self):
        """It should implement `has_indexes` class method.
        """
        for name, engine in service.engines.items():
            self.assertTrue(
                isinstance(engine.has_indexes(), bool),
                '%s does not implement `has_indexes` properly.' % name
            )

    @mock.patch.object(interface.EngineInterface, 'execute_query')
    def test_get_records(self, query):
        """EngineInterface.get_records should call db.Cursor.fetchall
        """
        expected = [('foo1', 'bar1',), ('foo2', 'bar2',)]
        statement = "SELECT foo, bar FROM public.acme"
        cursor_mock = mock.MagicMock(return_value=expected)
        query.return_value.__enter__.return_value.fetchall = cursor_mock

        for name, engine in self.engines.items():
            self.assertEqual(
                engine.get_records(statement),
                expected,
            )
            query.assert_called_with(statement, None)

    @mock.patch.object(interface.EngineInterface, 'execute_query')
    def test_get_first(self, query):
        """EngineInterface.get_records should call db.Cursor.fetchone
        """
        expected = ('foo1', 'bar1',)
        statement = "SELECT foo, bar FROM public.acme"
        cursor_mock = mock.MagicMock(return_value=expected)
        query.return_value.__enter__.return_value.fetchone = cursor_mock

        for name, engine in self.engines.items():
            self.assertEqual(
                engine.get_first(statement),
                expected,
            )
            query.assert_called_with(statement, None)

    @mock.patch.object(interface.EngineInterface, 'get_connection')
    def test_execute_query(self, get_connection):
        """EngineInterface.execute_query should call execute and return a Cursor.
        """
        statement = "SELECT foo, bar FROM public.acme"
        connection_context_mock = mock.MagicMock()
        get_connection.return_value = connection_context_mock

        for engine in self.engines.values():
            with engine.execute_query(statement) as cursor:
                cursor.execute.assert_called_with(statement)
                connection_context_mock.cursor.assert_called_with(**engine.cursor_kwargs)
                self.assertEqual(
                    cursor,
                    get_connection().cursor(),
                    'The returned cursor should be a cursor context manager.',
                )
