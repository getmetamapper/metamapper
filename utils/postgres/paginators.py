# -*- coding: utf-8 -*-
from django.core.paginator import Page, Paginator
from django.db import connections


class RawQuerySetPaginator(Paginator):
    """An efficient paginator for RawQuerySets.
    """
    def __init__(self, *args, **kwargs):
        super(RawQuerySetPaginator, self).__init__(*args, **kwargs)
        self.raw_query_set = self.object_list
        self.connection = connections[self.raw_query_set.db]
        self._count = None

    def _get_count(self):
        if self._count is None:
            cursor = self.connection.cursor()
            count_query = """SELECT COUNT(*) FROM (%s) AS sub_query_for_count""" % self.raw_query_set.raw_query
            cursor.execute(count_query, self.raw_query_set.params)
            self._count = cursor.fetchone()[0]
        return self._count
    count = property(_get_count)

    def _get_limit_offset_query(self, limit, offset):
        """mysql, postgresql, and sqlite can all use this syntax
        """
        return "SELECT * FROM (%s) as sub_query_for_pagination LIMIT %s OFFSET %s" % (self.raw_query_set.raw_query, limit, offset)

    def page(self, number):
        number = self.validate_number(number)
        offset = (number - 1) * self.per_page
        limit = self.per_page
        if offset + limit + self.orphans >= self.count:
            limit = self.count - offset
        query_with_limit = self._get_limit_offset_query(limit, offset)
        data = list(self.raw_query_set.model.objects.raw(query_with_limit, self.raw_query_set.params))
        return Page(data, number, self)
