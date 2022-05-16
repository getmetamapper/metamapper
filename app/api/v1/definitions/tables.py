# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from app.api.v1.exceptions import NotFound, ParameterValidationFailed
from app.api.v1.serializers import ApiSerializer
from app.api.v1.serializers import AssetOwnerSerializer, CustomPropertiesSerializer
from app.api.v1.serializers import AssetOwnersMixin, CustomPropertiesMixin
from app.api.v1.views import (
    BaseAPIView,
    CustomPropertyView,
    DetailAPIView,
    FindAPIView,
    ListAPIView,
    QueryParam,
)

from app.definitions.models import AssetOwner, Table

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


class TableProperties(GetTableMixin, CustomPropertyView):
    serializer_class = CustomPropertiesSerializer


class TableOwner(GetTableMixin, BaseAPIView):
    serializer_class = AssetOwnerSerializer

    def get_asset_owner(self, owner, content_object, *args, **kwargs):
        get_kwargs = {
            'object_id': content_object.id,
            'content_type': ContentType.objects.get_for_model(content_object),
            'owner_id': owner.id,
            'owner_type': ContentType.objects.get_for_model(owner),
            'workspace': self.request.workspace,
        }
        try:
            return AssetOwner.objects.get(**get_kwargs)
        except AssetOwner.DoesNotExist:
            raise NotFound()

    def get_data(self, table_id):
        """Parse required data from the Request.
        """
        request_data = self.request.data

        if 'owner_id' not in request_data or 'owner_type' not in request_data:
            raise ParameterValidationFailed()

        owner = None
        table = self.get_object(table_id)

        owner_id = request_data['owner_id']
        owner_type = request_data['owner_type'].upper()

        if owner_type == 'USER':
            owner = table.get_related_user(owner_id)
        elif owner_type == 'GROUP':
            owner = table.get_related_group(owner_id)

        if not owner:
            raise NotFound()

        return {'content_object': table, 'owner': owner}

    def post(self, request, pk):
        serializer = self.serializer_class(
            data=self.get_data(pk),
            context={'request': self.request})
        if serializer.is_valid():
            serializer.save(workspace=self.request.workspace)
            return self.format_response({'success': True})
        return self.format_errors(serializer.errors)

    def delete(self, request, pk, format=None):
        instance = self.get_asset_owner(**self.get_data(pk))
        instance.delete()
        return self.format_response({'success': True})


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
        r'^tables/(?P<pk>[a-f0-9]{32})/owners/?$',
        TableOwner.as_view(http_method_names=['post', 'delete']),
    ),
    url(
        r'^tables/(?P<pk>[a-f0-9]{32})/properties/?$',
        TableProperties.as_view(http_method_names=['patch', 'delete']),
    ),
]
