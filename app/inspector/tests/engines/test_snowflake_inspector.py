# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

import app.inspector.engines.snowflake_inspector as engine


class SnowflakeInspectorTests(unittest.TestCase):
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
        self.engine = engine.SnowflakeInspector(**self.connection)

    def test_not_have_indexes_sql(self):
        """It should NOT have `indexes_sql` attribute defined.
        """
        assert not engine.SnowflakeInspector.indexes_sql

    def test_has_definitions_sql(self):
        """It should have `definitions_sql` attribute defined.
        """
        assert isinstance(engine.SnowflakeInspector.definitions_sql, str)

    def test_get_tables_and_views_sql(self):
        """It should create the proper `tables_and_views_sql` where clause.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch)
        exc = """
        WHERE UPPER(t.table_catalog) = 'ACME'
          AND LOWER(c.table_schema) NOT IN (%s, %s, %s)
          AND (c.deleted IS NULL AND t.deleted IS NULL)
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
        exc = 'ORDER BY LOWER(c.table_schema), LOWER(c.table_name), c.ordinal_position'

        self.assertEqual(exc, sql[-len(exc):])

    def test_cursor_kwargs(self):
        """Snapshot test for cursor kwargs.
        """
        assert self.engine.cursor_kwargs == {
            'cursor_class': self.engine.dictcursor
        }

    def test_connect_kwargs(self):
        """It should alias the `host` attribute as `account`.
        """
        assert self.engine.connect_kwargs == {
            'account': 'localhost',
            'user': 'admin',
            'password': '1234567890',
            'database': 'acme',
            'login_timeout': 5,
        }

    def test_sys_schemas(self):
        """It should have the expected system table schemas.
        """
        assert set(self.engine.sys_schemas) == {
            'information_schema',
            'account_usage',
        }

    def test_has_indexes(self):
        """It should have indexes.
        """
        assert not engine.SnowflakeInspector.has_indexes()

    def test_get_indexes(self):
        """It should return an empty list.
        """
        assert not len(self.engine.get_indexes())

    @mock.patch.object(engine.SnowflakeInspector, 'get_first', return_value={'VERSION': '4.8.1'})
    def test_get_db_version(self, get_first):
        """It should implement Snowflake.get_db_version()
        """
        self.assertEqual(self.engine.get_db_version(), '4.8.1')

    @mock.patch.object(engine.SnowflakeInspector, 'get_db_version', return_value='4.8.1')
    def test_version(self, get_db_version):
        """It should implement Snowflake.version
        """
        self.assertEqual(self.engine.version, '4.8.1')
