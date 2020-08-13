# -*- coding: utf-8 -*-
import app.omnisearch.backends.base_search_backend as base

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F, Q, Value, Case, When
from django.db.models import CharField, DateTimeField
from django.db.models.functions import Cast

from django.utils.functional import cached_property

import app.omnisearch.stopwords as stopwords

from app.definitions.models import Table, Column
from app.comments.models import Comment
from app.revisioner.revisioners import get_content_types


class OrSearchQuery(SearchQuery):
    """Extension of SearchQuery to perform OR instead of AND operator.
    """
    def as_sql(self, compiler, connection):
        params = [self.value]
        function = self.SEARCH_TYPES[self.search_type]
        if self.config:
            config_sql, config_params = compiler.compile(self.config)
            template = '{}({}::regconfig, %s)'.format(function, config_sql)
            params = config_params + [self.value]
        else:
            template = "replace({}(%s)::text, '&', '|')::tsquery".format(function)
        if self.invert:
            template = '!!({})'.format(template)
        return template, params


class PostgresSearchBackend(base.BaseSearchBackend):
    """Postgres full-text search implementation (https://www.postgresql.org/docs/9.5/textsearch.html)
    """
    def search(self, search_query_string, **extra_filters):
        """Search the backend with a given query string. This needs to return the following signature:

        <QuerySet[
          {'pk': '...', 'model_name': '...', 'score': '...', 'datastore_id': '...'},
          ...
        ]>
        """
        adapter_classes = [
            ColumnModelSearchAdapter,
            CommentModelSearchAdapter,
            TableModelSearchAdapter,
        ]
        qs = None
        for adapter_class in adapter_classes:
            adapter = adapter_class(search_query_string)
            if not qs:
                qs = adapter.to_queryset(**extra_filters)
            else:
                qs = qs.union(adapter.to_queryset(**extra_filters))
        deduplicate_items = []
        deduplicate_ukeys = []
        for item in qs.order_by('-score'):
            ukey = '{model_name}-{pk}'.format(**item)
            if ukey in deduplicate_ukeys:
                continue
            deduplicate_items.append(item)
            deduplicate_ukeys.append(ukey)
        return deduplicate_items


class ModelSearchAdapter(object):
    """Base search adapter for any Django models.
    """
    model_class = None

    def __init__(self, query_string):
        self.query_string = query_string

    @property
    def base_queryset(self):
        return self.model_class.objects

    @cached_property
    def search_vector(self):
        return None

    @cached_property
    def search_query(self):
        return OrSearchQuery(self.query_string)

    def annotate_queryset(self, queryset):
        queryset = (
            queryset
                .annotate(search=self.search_vector)  # noqa
                .annotate(model_name=Value(self.model_class.__name__, CharField()))
                .annotate(score=SearchRank(self.search_vector, self.search_query))
                .annotate(pk=Cast('pk', CharField()))
        )
        return self.annotate_with_datastore(queryset)

    def filter_queryset(self, queryset):
        return queryset.filter(Q(search=self.search_query))

    def to_queryset(self, **extra_filters):
        return self.filter_queryset(
            self.annotate_queryset(self.base_queryset)
        ).filter(
            **extra_filters
        ).distinct().values('pk', 'model_name', 'score', 'datastore_id')


class TrigramSimilarityMixin(object):
    """This mixin splits the query string and does a trigram similiary (read: distance check) between
    a provided trigram_field and each word in the query string.
    """
    trigram_field = None

    def annotate_queryset(self, queryset):
        queryset = super().annotate_queryset(queryset)

        for i, word in enumerate(self.query_string.split(' ')):
            if word in stopwords.english:
                continue
            queryset = queryset.annotate(**{'similarity_%s' % i: TrigramSimilarity(self.trigram_field, word)})

        return queryset

    def filter_queryset(self, queryset):
        filters = Q(search=self.query_string) | Q(search__icontains=self.query_string)

        for i, word in enumerate(self.query_string.split(' ')):
            if word in stopwords.english:
                continue
            filters |= Q(**{'similarity_%s__gte' % i: 0.3})

        return queryset.filter(filters)


class TableModelSearchAdapter(TrigramSimilarityMixin, ModelSearchAdapter):
    """Search adapter for the Table model.
    """
    model_class = Table

    trigram_field = 'name'

    @property
    def base_queryset(self):
        return self.model_class.objects.annotate(property=F('table_properties__value'))

    @cached_property
    def search_vector(self):
        a = SearchVector('name', 'short_desc', weight='A')
        b = SearchVector('tags', 'property', weight='B')
        c = SearchVector('schema__name', weight='C')
        return (a + b + c)

    def annotate_with_datastore(self, queryset):
        """Add the datastore to the query, which will be used to filter if necessary.
        """
        return queryset.annotate(datastore_id=F('schema__datastore_id'))


class ColumnModelSearchAdapter(TrigramSimilarityMixin, ModelSearchAdapter):
    """Search adapter for the Column model.
    """
    model_class = Column

    trigram_field = 'name'

    @cached_property
    def search_vector(self):
        return SearchVector('name', 'short_desc')

    def annotate_with_datastore(self, queryset):
        """Add the datastore to the query, which will be used to filter if necessary.
        """
        return queryset.annotate(datastore_id=F('table__schema__datastore_id'))


class CommentModelSearchAdapter(ModelSearchAdapter):
    """Search adapter for the Comment model.
    """
    model_class = Comment

    @cached_property
    def content_types(self):
        return get_content_types()

    @cached_property
    def search_vector(self):
        return SearchVector('text')

    @property
    def base_queryset(self):
        case_statement_1 = Case(
            When(content_type=self.content_types['Table'], then=F('table__id')),
            When(content_type=self.content_types['Column'], then=F('column__id')),
            output_field=DateTimeField(),
        )
        case_statement_2 = Case(
            When(content_type=self.content_types['Table'], then=F('table__deleted_at')),
            When(content_type=self.content_types['Column'], then=F('column__deleted_at')),
            output_field=CharField(),
        )
        return (
            self.model_class
                .objects
                .annotate(object_ident=case_statement_1)
                .annotate(object_deleted_at=case_statement_2)
                .filter(object_ident__isnull=False)
                .filter(object_deleted_at=None)
        )

    def annotate_with_datastore(self, queryset):
        """Add the datastore to the query, which will be used to filter if necessary.
        """
        case_statement = Case(
            When(content_type=self.content_types['Table'], then=F('table__schema__datastore_id')),
            When(content_type=self.content_types['Column'], then=F('column__table__schema__datastore_id')),
            default=Value(""),
            output_field=CharField(),
        )
        return queryset.annotate(datastore_id=case_statement)
