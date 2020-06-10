# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
)


def SearchManager(fields):
    """Decorator for search manager.
    """
    if not isinstance(fields, (tuple, list)):
        raise TypeError('SearchManager requires a list of searchable fields.')

    class InnerSearchManager(models.Manager):
        _fields = fields

        def execute(self, search=None, *args, **kwargs):
            """Execute Postgres full-text search on a set of fields.
            """
            qs = self.get_queryset()
            if search:
                query = SearchQuery(search)
                vector = SearchVector(*self._fields)
                qs = qs.annotate(search=vector)\
                       .filter(search__icontains=search)\
                       .annotate(rank=SearchRank(vector, query))\
                       .order_by('-rank')
            qs = qs.filter(**kwargs)
            return qs

    return InnerSearchManager()
