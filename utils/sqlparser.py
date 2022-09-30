# -*- coding: utf-8 -*-
from sql_metadata import Parser as BaseParser
from collections import namedtuple


Session = namedtuple('Session', [
    'database',
    'schema',
    'user',
])


def try_get(parts, idx):
    try:
        return parts[idx]
    except IndexError:
        return None


class Parser(BaseParser):
    """Override Parser class from `sql_metadata` to introduce additional logic.
    """
    def __init__(self, *args, db_session, **kwargs):
        super().__init__(*args, **kwargs)
        self.db_session = db_session

    def get_tables(self):
        """Retrieve table objects.
        """
        output = []
        for table in map(str.lower, self.tables):
            parts = table.split('.')
            stuff = {
                'db': try_get(parts, -3) or self.db_session.database,
                'db_schema': try_get(parts, -2) or self.db_session.schema,
                'db_table': try_get(parts, -1),
            }
            output.append(stuff)
        return output
