# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import DetailAPIView, FindAPIView, ListAPIView, QueryParam

from app.definitions.models import Column

from utils.fields import SortedListField
from utils.shortcuts import clean_html


class ColumnSerializer(ApiSerializer):
    id = serializers.SerializerMethodField()

    short_desc = serializers.CharField(
        max_length=140,
        allow_null=True,
        allow_blank=True,
        trim_whitespace=True,
        required=False,
    )

    tags = SortedListField(
        child=serializers.CharField(max_length=30),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    readme = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta:
        model = Column
        fields = [
            'id',
            'name',
            'short_desc',
            'tags',
            'readme',
            'ordinal_position',
            'data_type',
            'max_length',
            'numeric_scale',
            'is_primary',
            'is_nullable',
            'default_value',
            'created_at',
            'updated_at',
        ]
        writable_fields = ['short_desc', 'tags', 'readme']

    def get_id(self, obj):
        return obj.object_id

    def validate_tags(self, tags):
        """We should remove any duplicate tags that exist.
        """
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    def validate_readme(self, readme):
        """We should convert null readme to blank.
        """
        return clean_html('' if readme is None else readme)

    def update(self, instance, validated_data):
        instance.tags = validated_data.get('tags', instance.tags)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        instance.readme = validated_data.get('readme', instance.readme)
        instance.save()
        return instance


class ColumnList(ListAPIView):
    serializer_class = ColumnSerializer

    def get_queryset(self):
        filter_kwargs = {
            'table_id': self.kwargs['table_id'],
            'workspace': self.request.workspace,
        }
        return Column.objects.filter(**filter_kwargs).order_by('ordinal_position')


class ColumnDetail(DetailAPIView):
    serializer_class = ColumnSerializer

    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'object_id': pk,
        }
        try:
            return Column.objects.get(**get_kwargs)
        except Column.DoesNotExist:
            raise NotFound()


class ColumnFind(FindAPIView):
    serializer_class = ColumnSerializer

    allowed_query_params = [
        QueryParam('schema', required=True),
        QueryParam('table', required=True),
        QueryParam('name', required=True),
    ]

    def find_object(self, datastore_id, query_params):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'table__schema__datastore_id': datastore_id,
            'table__schema__name': query_params['schema'],
            'table__name': query_params['table'],
            'name': query_params['name'],
        }
        return Column.objects.filter(**filter_kwargs).first()


urlpatterns = [
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/columns/find/?$',
        ColumnFind.as_view(),
    ),
    url(
        r'^tables/(?P<table_id>[a-f0-9]{32})/columns/?$',
        ColumnList.as_view(),
    ),
    url(
        r'^columns/(?P<pk>[a-f0-9]{32})/?$',
        ColumnDetail.as_view(),
    ),
]
