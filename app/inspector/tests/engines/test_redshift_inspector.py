# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

import app.inspector.engines.redshift_inspector as engine


VERSION = (
    'PostgreSQL 8.0.2 on i686-pc-linux-gnu, '
    'compiled by GCC gcc (GCC) 3.4.2 20041017 '
    '(Red Hat 3.4.2-6.fc3), Redshift 1.0.12103'
)


class RedshiftInspectorTests(unittest.TestCase):
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
