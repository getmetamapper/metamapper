# -*- coding: utf-8 -*-
import app.definitions.models as models
import utils.graphql.filters as filters


class DataAssetsFilterSet(filters.FilterSet):
    """Filtering capabilities for data assets listings.
    """
    schema = filters.CharFilter(field_name='schema__name', lookup_expr='iexact')

    class Meta:
        model = models.Table
        fields = []
