# -*- coding: utf-8 -*-
import app.revisioner.models as models
import utils.graphql.filters as filters


class RevisionFilterSet(filters.FilterSet):
    """Filtering capabilities for reivion changes interface.
    """
    actions = filters.MultipleChoiceFilter(
        field_name='action',
        choices=models.Revision.ACTION_CHOICES,
    )

    types = filters.MultipleChoiceFilter(
        field_name='resource_type__model',
        choices=(('schema', 'schema'), ('table', 'table'), ('column', 'column'), ('index', 'index')),
    )

    search = filters.CharFilter(
        field_name='metadata__name',
        lookup_expr='icontains',
    )

    class Meta:
        model = models.Revision
        fields = []
