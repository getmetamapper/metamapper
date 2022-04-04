# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer, AssetOwnersMixin, CustomPropertiesMixin
from app.api.v1.views import (
    BaseAPIView,
    DetailAPIView,
    FindAPIView,
    ListAPIView,
    QueryParam,
)

from app.definitions.models import Table

from utils.fields import SortedListField
from utils.shortcuts import clean_html, omit


class GetTableMixin(object):
    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'object_id': pk,
        }
        try:
            return Table.objects.get(**get_kwargs)
        except Table.DoesNotExist:
            raise NotFound()


class TableSerializer(ApiSerializer):
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
        model = Table
        fields = [
            'id',
            'name',
            'kind',
            'short_desc',
            'tags',
            'readme',
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


class TableDetailSerializer(AssetOwnersMixin, CustomPropertiesMixin, TableSerializer):
    class Meta(TableSerializer.Meta):
        fields = omit(TableSerializer.Meta.fields, ['created_at', 'updated_at']) + [
            'owners',
            'properties',
            'created_at',
            'updated_at',
        ]


class DatastoreTableList(ListAPIView):
    serializer_class = TableSerializer

    def get_queryset(self):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'schema__datastore_id': self.kwargs['datastore_id'],
        }
        return Table.objects.filter(**filter_kwargs)


class TableList(ListAPIView):
    serializer_class = TableSerializer

    def get_queryset(self):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'schema_id': self.kwargs['schema_id'],
        }
        return Table.objects.filter(**filter_kwargs)


class TableDetail(GetTableMixin, DetailAPIView):
    serializer_class = TableDetailSerializer


class TableFind(FindAPIView):
    serializer_class = TableDetailSerializer

    allowed_query_params = [
        QueryParam('schema', required=True),
        QueryParam('name', required=True),
    ]

    def find_object(self, datastore_id, query_params):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'schema__datastore_id': datastore_id,
            'schema__name': query_params['schema'],
            'name': query_params['name'],
        }
        return Table.objects.filter(**filter_kwargs).first()


class TableOwners(GetTableMixin, BaseAPIView):
    serializer_class = TableSerializer

    def create(self, request, table_id, format=None):
        pass

    def destroy(self, request, table_id, format=None):
        pass


class TableProperties(GetTableMixin, BaseAPIView):
    serializer_class = TableSerializer

    def create(self, request, table_id, format=None):
        pass

    def destroy(self, request, table_id, format=None):
        pass


urlpatterns = [
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/tables/?$',
        DatastoreTableList.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/tables/find/?$',
        TableFind.as_view(),
    ),
    url(
        r'^schemas/(?P<schema_id>[a-f0-9]{32})/tables/?$',
        TableList.as_view(),
    ),
    url(
        r'^tables/(?P<pk>[a-f0-9]{32})/?$',
        TableDetail.as_view(),
    ),
    url(
        r'^tables/(?P<table_id>[a-f0-9]{32})/owners/?$',
        TableOwners.as_view(http_method_names=['get', 'post']),
    ),
    url(
        r'^tables/(?P<table_id>[a-f0-9]{32})/properties/?$',
        TableProperties.as_view(http_method_names=['get', 'post']),
    ),
]
