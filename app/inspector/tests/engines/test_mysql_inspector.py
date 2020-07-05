# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

import app.inspector.engines.mysql_inspector as engine


class MySQLInspectorTests(unittest.TestCase):
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

    def test_get_tables_and_views_sql(self):
        """It should create the proper `tables_and_views_sql` where clause.
        """
        sch = ['one', 'two', 'three']
        sql = self.engine.get_tables_and_views_sql(sch)
        exc = '''
        WHERE t.engine = 'InnoDB'
          AND t.table_schema NOT IN (%s, %s, %s)
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
        WHERE t.engine = 'InnoDB'
          AND t.table_schema NOT IN (%s, %s)
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
