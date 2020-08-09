# -*- coding: utf-8 -*-
import re
import unittest.mock as mock

from django import test
from django.utils import timezone

import app.inspector.engines.mysql_inspector as engine
import app.revisioner.tasks.core as coretasks

import testutils.factories as factories


class MySQLInspectorInterfaceTests(test.TestCase):
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
        self.engine = engine.MySQLInspector(**self.connection)

    def test_has_indexes_sql(self):
        """It should have `indexes_sql` attribute defined.
        """
        assert isinstance(engine.MySQLInspector.indexes_sql, str)

    def test_has_definitions_sql(self):
        """It should have `definitions_sql` attribute defined.
        """
        assert isinstance(engine.MySQLInspector.definitions_sql, str)

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '5.7.0'})
    def test_get_tables_and_views_sql(self, get_first):
        """It should create the proper `tables_and_views_sql` where clause.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch)
        exc = '''
        WHERE t.table_schema NOT IN (%s, %s, %s)
        '''
        self.assertIn(
            ''.join(exc.split()).strip(),
            ''.join(sql.split()).strip(),
        )

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '5.7.0'})
    def test_get_tables_and_views_sql_ordered(self, get_first):
        """The Revisioner depends on the data coming in a specific order.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch).replace('\n', '')
        exc = 'ORDER BY c.table_schema, c.table_name, c.ordinal_position'

        self.assertEqual(exc, sql[-len(exc):])

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '5.7.0'})
    def test_get_indexes_sql(self, get_first):
        """It should create the proper `indexes_sql` where clause.
        """
        sch = ['one', 'two']
        sql = self.engine.get_indexes_sql(sch)
        exc = '''
        WHERE t.table_schema NOT IN (%s, %s)
        '''
        self.assertIn(
            ''.join(exc.split()).strip(),
            ''.join(sql.split()).strip(),
        )

    def test_cursor_kwargs(self):
        """Snapshot test for cursor kwargs.
        """
        assert self.engine.cursor_kwargs == {
            'cursor_class': self.engine.dictcursor
        }

    def test_sys_schemas(self):
        """It should have the expected system table schemas.
        """
        assert set(self.engine.sys_schemas) == {
            'information_schema',
            'mysql',
            'performance_schema',
            'sys',
        }

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert engine.MySQLInspector.has_indexes()

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '9.6.0'})
    def test_get_db_version(self, get_first):
        """It should implement MySQL.get_db_version()
        """
        self.assertEqual(self.engine.get_db_version(), '9.6.0')

    @mock.patch.object(engine.MySQLInspector, 'get_db_version', return_value='10.1.2')
    def test_version(self, get_db_version):
        """It should implement MySQL.version
        """
        self.assertEqual(self.engine.version, '10.1.2')

    def test_connect_kwargs(self):
        """It should have the connect timeout parameter.
        """
        assert self.engine.connect_kwargs == {
            'host': 'localhost',
            'user': 'admin',
            'password': '1234567890',
            'port': 3306,
            'database': 'acme',
            'connect_timeout': 5,
        }


class MySQLInspectorIntegrationTestMixin(object):
    """Test cases that hit a live database spun up via Docker.
    """
    hostname = None

    schema_count = 3

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'metamapper_ro',
            'password': '340Uuxwp7Mcxo7Khy',
            'port': 3306,
            'database': 'employees',
        }

    def get_inspector(self):
        return engine.MySQLInspector(**self.get_connection())

    def test_verify_connection(self):
        """It can connect to MySQL using the provided credentials.
        """
        self.assertTrue(
            self.get_inspector().verify_connection(),
            'Host: %s' % self.hostname,
        )

    def test_tables_and_views(self):
        """It should return the correct table and view response.
        """
        records = self.get_inspector().get_tables_and_views()
        schemas = set()

        table_items = []
        table_types = set()

        column_items = []

        for record in records:
            schemas.add((record['schema_object_id'], record['table_schema']))

            # It should have unique table identities.
            self.assertTrue(record['table_object_id'])
            self.assertTrue(record['table_object_id'] not in table_items)
            table_items.append(record['table_object_id'])
            table_types.add(record['table_type'])

            # It should have unique column identities.
            for column in record['columns']:
                self.assertTrue(column['column_object_id'])
                self.assertTrue(column['column_object_id'] not in column_items)
                column_items.append(column['column_object_id'])

        # Each schema should have a unique identity.
        self.assertEqual(len(schemas), self.schema_count)
        self.assertEqual(table_types, {'base table', 'view'})

    def test_indexes(self):
        """It should return the correct index response.
        """
        records = self.get_inspector().get_indexes()
        schemas = set()

        index_items = []
        column_items = []

        for record in records:
            schemas.add((record['schema_object_id'], record['schema_name']))

            # It should have unique index identities.
            self.assertTrue(record['index_object_id'])
            self.assertTrue(record['index_object_id'] not in index_items)
            index_items.append(record['index_object_id'])

        # Each schema should have a unique identity.
        self.assertEqual(len(schemas), self.schema_count)

    def test_get_db_version(self):
        """It should return the correct version.
        """
        self.assertTrue(
            re.match(self.version_regexp, self.get_inspector().get_db_version()),
            'Host: %s' % self.hostname,
        )

    def test_initial_revisioner_run(self):
        """It should be able to commit the initial run to the metastore.
        """
        datastore = factories.DatastoreFactory(engine='mysql', **self.get_connection())

        run = datastore.run_history.create(
            workspace_id=datastore.workspace_id,
            started_at=timezone.now(),
        )

        coretasks.start_revisioner_run(run.id)

        run.refresh_from_db()

        self.assertTrue(run.finished_at is not None)
        self.assertEqual(run.errors.count(), 0)
        self.assertEqual(datastore.schemas.count(), self.schema_count)


@test.tag('mysql', 'inspector')
class MySQLFivePointSixIntegrationTests(MySQLInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for MySQL v5.6
    """
    hostname = 'mysql-5.6'

    version_regexp = r'5\.6\.[0-9]{1,3}'


@test.tag('mysql', 'inspector')
class MySQLFivePointSevenIntegrationTests(MySQLInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for MySQL v5.7
    """
    hostname = 'mysql-5.7'

    version_regexp = r'5\.7\.[0-9]{1,3}'


@test.tag('mysql', 'inspector')
class MySQLEightPointZeroIntegrationTests(MySQLInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for MySQL v8.0
    """
    hostname = 'mysql-8.0'

    version_regexp = r'8\.0\.[0-9]{1,3}'
