# -*- coding: utf-8 -*-
import app.definitions.models as models
import utils.graphql.filters as filters


class DataAssetsFilterSet(filters.FilterSet):
    """Filtering capabilities for data assets listings.
    """
    schema = filters.CharFilter(field_name='schema__name', lookup_expr='iexact')

    order_by = filters.OrderingFilter(
        fields=(
            ('schema__name', 'schema'),
            ('name', 'table'),
            ('usage_score', 'popularity'),
        )
    )

    class Meta:
        model = models.Table
        fields = []
