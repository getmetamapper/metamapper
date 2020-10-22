# -*- coding: utf-8 -*-
import unittest.mock as mock

from django import test
from django.utils import timezone

import app.inspector.engines.redshift_inspector as engine
import app.revisioner.tasks.core as coretasks

import testutils.factories as factories


VERSION = (
    'PostgreSQL 8.0.2 on i686-pc-linux-gnu, '
    'compiled by GCC gcc (GCC) 3.4.2 20041017 '
    '(Red Hat 3.4.2-6.fc3), Redshift 1.0.12103'
)


class RedshiftInspectorTests(test.TestCase):
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
        self.engine = engine.RedshiftInspector(**self.connection)

    def test_not_have_indexes_sql(self):
        """It should NOT have `indexes_sql` attribute defined.
        """
        assert not engine.RedshiftInspector.indexes_sql

    def test_has_definitions_sql(self):
        """It should have `definitions_sql` attribute defined.
        """
        assert isinstance(engine.RedshiftInspector.definitions_sql, str)

    def test_get_tables_and_views_sql(self):
        """It should create the proper `tables_and_views_sql` where clause.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch)
        exc = """
        WHERE ns.nspname NOT IN (%s, %s, %s)
          AND ns.nspname NOT LIKE 'pg_temp%%'
          AND ns.nspname NOT LIKE 'pg_am%%'
          AND a.attnum > 0
          AND c.relkind in ('r', 'v', 'm')
        """
        self.assertIn(
            ''.join(exc.split()).strip(),
            ''.join(sql.split()).strip(),
        )

    def test_get_tables_and_views_sql_ordered(self):
        """The Revisioner depends on the data coming in a specific order.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch).replace('\n', '')
        exc = 'ORDER BY ns.nspname, c.relname, a.attnum'

        self.assertEqual(exc, sql[-len(exc):])

    def test_cursor_kwargs(self):
        """Snapshot test for cursor kwargs.
        """
        assert self.engine.cursor_kwargs == {
            'cursor_factory': self.engine.dictcursor
        }

    def test_sys_schemas(self):
        """It should have the expected system table schemas.
        """
        assert set(self.engine.sys_schemas) == {
            'information_schema',
            'pg_catalog',
            'pg_internal',
        }

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert not engine.RedshiftInspector.has_indexes()

    def test_get_indexes(self):
        """It should return an empty list.
        """
        assert not len(self.engine.get_indexes())

    @mock.patch.object(engine.RedshiftInspector, 'get_first', return_value={'version': VERSION})
    def test_get_db_version(self, get_first):
        """It should implement Redshift.get_db_version()
        """
        self.assertEqual(self.engine.get_db_version(), '1.0.12103')

    @mock.patch.object(engine.RedshiftInspector, 'get_db_version', return_value='1.0.12103')
    def test_version(self, get_db_version):
        """It should implement Redshift.version
        """
        self.assertEqual(self.engine.version, '1.0.12103')


class RedshiftInspectorIntegrationTestMixin(object):
    """Test cases that hit a live database spun up via Docker.
    """
    hostname = None

    schema_count = 3

    def get_connection(self):
        return {
            'host': self.hostname,
            'username': 'metamapper_ro',
            'password': '340Uuxwp7Mcxo7Khy',
            'port': 5439,
            'database': 'postgres',
        }

    def get_inspector(self):
        return engine.RedshiftInspector(**self.get_connection())

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
        self.assertEqual(self.get_inspector().get_indexes(), [])

    def test_get_db_version(self):
        """We're testing against Postgres 8.0, so we can't literally confirm
        the version. But this more-or-less confirms that we can execute the query.
        """
        self.get_inspector().get_db_version()

    def test_initial_revisioner_run(self):
        """It should be able to commit the initial run to the metastore.
        """
        datastore = factories.DatastoreFactory(engine='redshift', **self.get_connection())

        run = datastore.run_history.create(
            workspace_id=datastore.workspace_id,
            started_at=timezone.now(),
        )

        coretasks.start_revisioner_run(run.id)

        run.refresh_from_db()

        self.assertTrue(run.finished_at is not None)
        self.assertEqual(run.errors.count(), 0)
        self.assertEqual(datastore.schemas.count(), self.schema_count)

    def test_get_last_commit_time_for_table(self):
        """It should implement Redshift.get_last_commit_time_for_table
        """
        self.assertEqual(self.engine.get_last_commit_time_for_table('public', 'accounts'), None)


@test.tag('redshift', 'inspector')
class RedshiftIntegrationTests(RedshiftInspectorIntegrationTestMixin, test.TestCase):
    """Integration tests for Oracle 12c
    """
    hostname = 'redshift'
