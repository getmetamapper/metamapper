# -*- coding: utf-8 -*-
from django.db.models import expressions


class HStoreValue(expressions.Expression):
    """Represents a HStore value.

    The base PostgreSQL implementation Django provides, always
    represents HStore values as dictionaries, but this doesn't work if
    you want to use expressions inside hstore values.
    """
    def __init__(self, value):
        """Initializes a new instance.
        """
        self.value = value

    def resolve_expression(self, *args, **kwargs):
        """Resolves expressions inside the dictionary.
        """
        result = dict()
        for key, value in self.value.items():
            if hasattr(value, "resolve_expression"):
                result[key] = value.resolve_expression(*args, **kwargs)
            else:
                result[key] = value
        return HStoreValue(result)

    def as_sql(self, compiler, connection):
        """Compiles the HStore value into SQL.

        Compiles expressions contained in the values
        of HStore entries as well.

        Given a dictionary like:
            dict(key1='val1', key2='val2')

        The resulting SQL will be:
            hstore(hstore('key1', 'val1'), hstore('key2', 'val2'))
        """
        result = []
        for key, value in self.value.items():
            if hasattr(value, "as_sql"):
                sql, params = value.as_sql(compiler, connection)
                result.append("hstore('%s', %s)" % (key, sql % params))
            elif value is not None:
                result.append("hstore('%s', '%s')" % ((key, value)))
            else:
                result.append("hstore('%s', NULL)" % key)
        return "%s" % " || ".join(result), []
