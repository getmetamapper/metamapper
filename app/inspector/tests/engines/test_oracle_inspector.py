# -*- coding: utf-8 -*-
import unittest.mock as mock

from django import test
from django.utils import timezone

import app.inspector.engines.oracle_inspector as engine
import app.revisioner.tasks.core as coretasks

import testutils.factories as factories


class OracleInspectorTests(test.TestCase):
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
        self.engine = engine.OracleInspector(**self.connection)

    def test_has_indexes_sql(self):
        """It should have `indexes_sql` attribute defined.
        """
        assert isinstance(engine.OracleInspector.indexes_sql, str)

    def test_get_tables_and_views_sql(self):
        """It should create the proper `tables_and_views_sql` where clause.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch)
        exc = '''
        WHERE LOWER(T.OBJECT_TYPE) IN ('table', 'view')
          AND LOWER(T.OWNER) NOT IN (:1, :2, :3)
        '''
        self.assertIn(
            ''.join(exc.split()).strip(),
            ''.join(sql.split()).strip(),
        )

    def test_get_indexes_sql(self):
        """It should create the proper `indexes_sql` where clause.
        """
        sch = ['one', 'two']
        sql = self.engine.get_indexes_sql(sch)
        exc = '''
        WHERE LOWER(I.OBJECT_TYPE) IN ('index')
          AND LOWER(I.OWNER) NOT IN (:1, :2)
        '''
        self.assertIn(
            ''.join(exc.split()).strip(),
            ''.join(sql.split()).strip(),
        )

    def test_has_definitions_sql(self):
        """It should have `definitions_sql` attribute defined.
        """
        assert isinstance(engine.OracleInspector.definitions_sql, str)

    def test_assertion_query(self):
        """Snapshot check for the `assertion_query` attribute.
        """
        assert self.engine.assertion_query == (
            "SELECT 1 as assertion FROM DBA_OBJECTS WHERE ROWNUM = 1"
        )

    def test_sys_schemas(self):
        """It should have the expected system table schemas.
        """
        assert set(self.engine.sys_schemas) == {
            'apex_030200',
            'apex_050000',
            'appqossys',
            'audsys',
            'ctxsys',
            'dbsfwuser',
            'dbsnmp',
            'dvsys',
            'exfsys',
            'flows_files',
            'gsmadmin_internal',
            'lbacsys',
            'mdsys',
            'ojvmsys',
            'olapsys',
            'orddata',
            'ordsys',
            'outln',
            'rdsadmin',
            'sys',
            'sysaux',
            'sysman',
            'system',
            'tsmsys',
            'wmsys',
            'xdb',
        }

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert engine.OracleInspector.has_indexes()

    @mock.patch.object(engine.OracleInspector, 'get_first', return_value={'banner': '9.6.0'})
    def test_get_db_version(self, get_first):
        """It should implement Oracle.get_db_version()
        """
        self.assertEqual(self.engine.get_db_version(), '9.6.0')

    @mock.patch.object(engine.OracleInspector, 'get_db_version', return_value='10.1.2')
    def test_version(self, get_db_version):
        """It should implement Oracle.version
        """
        self.assertEqual(self.engine.version, '10.1.2')


class OracleInspectorIntegrationTestMixin(object):
    """Test cases that hit a live database spun up via Docker.
    """
    hostname = None

    schema_count = 3

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'metamapper',
            'password': 'pwd4smithj',
            'port': 1521,
            'database': 'testing',
        }

    def get_inspector(self):
        return engine.OracleInspector(**self.get_connection())

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
        self.assertEqual(table_types, {'table', 'view'})

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
        self.assertIn(
            'Oracle Database 12c',
            self.get_inspector().get_db_version(),
        )

    def test_initial_revisioner_run(self):
        """It should be able to commit the initial run to the metastore.
        """
        datastore = factories.DatastoreFactory(engine='oracle', **self.get_connection())

        run = datastore.run_history.create(
            workspace_id=datastore.workspace_id,
            started_at=timezone.now(),
        )

        coretasks.start_revisioner_run(run.id)

        run.refresh_from_db()

        self.assertTrue(run.finished_at is not None)
        self.assertEqual(run.errors.count(), 0)
        self.assertEqual(datastore.schemas.count(), self.schema_count)


@test.tag('oracle', 'inspector')
class Oracle12cIntegrationTests(OracleInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for Oracle 12c
    """
    hostname = 'oracle-12c'
