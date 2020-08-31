# -*- coding: utf-8 -*-
import unittest.mock as mock

from django import test
from django.utils import timezone

import app.inspector.engines.mysql_inspector as engine
import app.revisioner.tasks.core as coretasks

import testutils.factories as factories

import app.inspector.engines.hive_metastore_inspector as engine


class HiveMetastoreInspectorTests(test.TestCase):
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

        self.engine = engine.HiveMetastoreInspector(
            extras={'dialect': 'mysql'},
            **self.connection,
        )

    def test_inspector_attribute(self):
        """It should inherit the provided inspector class.
        """
        for dialect, inspector_class in engine.supported_external_metastores.items():
            instance = engine.HiveMetastoreInspector(
                extras={'dialect': dialect},
                **self.connection,
            )
            assert isinstance(instance.inspector, inspector_class)


    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '5.7.0'})
    def test_get_tables_and_views_sql_inherited(self, get_first):
        """It should override the inherited inspector SQL.
        """
        self.assertEqual(
            self.engine.inspector.get_tables_and_views_sql([]),
            engine.HIVE_METASTORE_DEFINITIONS_QUERY,
        )

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'version': '5.7.0'})
    def test_get_tables_and_views_sql_ordered(self, get_first):
        """The Revisioner depends on the data coming in a specific order.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.inspector.get_tables_and_views_sql(sch).replace('\n', '')
        exc = 'ORDER by table_schema, table_name, ordinal_position'

        self.assertEqual(exc, sql[-len(exc):])

    def test_sys_schemas(self):
        """It should have the expected system table schemas.
        """
        assert set(self.engine.sys_schemas) == set()
        assert set(self.engine.inspector.sys_schemas) == set()

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert not engine.HiveMetastoreInspector.has_indexes()

    def test_get_indexes(self):
        """It should return an empty list.
        """
        assert not len(self.engine.get_indexes())

    @mock.patch.object(engine.MySQLInspector, 'get_first', return_value={'SCHEMA_VERSION': '4.8.1'})
    def test_get_db_version(self, get_first):
        """It should implement HiveMetastoreInspector.get_db_version()
        """
        self.assertEqual(self.engine.get_db_version(), '4.8.1')

    @mock.patch.object(engine.HiveMetastoreInspector, 'get_db_version', return_value='4.8.1')
    def test_version(self, get_db_version):
        """It should implement Snowflake.version
        """
        self.assertEqual(self.engine.version, '4.8.1')



class HiveMetastoreInspectorIntegrationTestMixin(object):
    """Test cases that hit a live database spun up via Docker.
    """
    hostname = None

    schema_count = 5

    def get_inspector(self):
        return engine.HiveMetastoreInspector(**self.get_connection())

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
        self.assertEqual(table_types, {'VIRTUAL_VIEW', 'EXTERNAL_TABLE', 'MANAGED_TABLE'})

    def test_get_db_version(self):
        """It should return the correct version.
        """
        self.assertEqual(
            self.get_inspector().get_db_version(),
            '2.3.0',
            'Host: %s' % self.hostname,
        )

    def test_initial_revisioner_run(self):
        """It should be able to commit the initial run to the metastore.
        """
        datastore = factories.DatastoreFactory(engine='hive', **self.get_connection())

        run = datastore.run_history.create(
            workspace_id=datastore.workspace_id,
            started_at=timezone.now(),
        )

        coretasks.start_revisioner_run(run.id)

        run.refresh_from_db()

        self.assertTrue(run.finished_at is not None)
        self.assertEqual(run.errors.count(), 0)
        self.assertEqual(datastore.schemas.count(), self.schema_count)


@test.tag('hive', 'inspector')
class HiveMySQLIntegrationTests(HiveMetastoreInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for MySQL metastore.
    """
    hostname = 'mysql-hive-2.3.0'

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'root',
            'password': 'example',
            'port': 3306,
            'database': 'hive_metastore',
            'extras': {'dialect': 'mysql'},
        }


@test.tag('hive', 'inspector')
class HivePostgreSQLIntegrationTests(HiveMetastoreInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for Postgres metastore.
    """
    hostname = 'postgresql-hive-2.3.0'

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'postgres',
            'password': 'postgres',
            'port': 5432,
            'database': 'hive_metastore',
            'extras': {'dialect': 'postgresql'},
        }


@test.tag('hive', 'inspector')
class HiveSQLServerIntegrationTests(HiveMetastoreInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for MS SQL metastore.
    """
    hostname = 'sqlserver-hive-2.3.0'

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'sa',
            'password': '6095A5f58910e18a4c8',
            'port': 1433,
            'database': 'master',
            'extras': {'dialect': 'sqlserver'},
        }
