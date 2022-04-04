# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer, AssetOwnersMixin, CustomPropertiesMixin
from app.api.v1.views import BaseAPIView, DetailAPIView, ListAPIView

from app.definitions.models import Datastore

from utils.fields import SortedListField
from utils.shortcuts import omit


class GetDatastoreMixin(object):
    def get_object(self, id):
        get_kwargs = {
            'workspace': self.request.workspace,
            'id': id,
        }
        try:
            return Datastore.objects.get(**get_kwargs)
        except Datastore.DoesNotExist:
            raise NotFound()


class DatastoreSerializer(ApiSerializer):
    is_enabled = serializers.BooleanField()
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

    class Meta:
        model = Datastore
        fields = [
            'id',
            'name',
            'slug',
            'engine',
            'version',
            'is_enabled',
            'short_desc',
            'tags',
            'created_at',
            'updated_at',
        ]
        writable_fields = ['is_enabled', 'tags', 'short_desc']

    def validate_short_desc(self, short_desc):
        """We should convert null descriptions to blank.
        """
        return '' if short_desc is None else short_desc

    def validate_tags(self, tags):
        """We should remove any duplicate tags that exist.
        """
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def update(self, instance, validated_data):
        instance.is_enabled = validated_data.get('is_enabled', instance.is_enabled)
        instance.short_desc = validated_data.get('short_desc', instance.short_desc)
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance


class DatastoreDetailSerializer(CustomPropertiesMixin, DatastoreSerializer):
    class Meta(DatastoreSerializer.Meta):
        fields = omit(DatastoreSerializer.Meta.fields, ['created_at', 'updated_at']) + [
            'properties',
            'created_at',
            'updated_at',
        ]


class DatastoreList(ListAPIView):
    serializer_class = DatastoreSerializer

    def get_queryset(self):
        filter_kwargs = {
            'workspace': self.request.workspace,
        }
        return Datastore.objects.filter(**filter_kwargs)


class DatastoreDetail(GetDatastoreMixin, DetailAPIView):
    serializer_class = DatastoreDetailSerializer


class DatastoreProperties(GetDatastoreMixin, BaseAPIView):
    serializer_class = DatastoreSerializer

    def create(self, request, datastore_id, format=None):
        pass

    def destroy(self, request, datastore_id, format=None):
        pass


urlpatterns = [
    url(
        r'^datastores/?$',
        DatastoreList.as_view(),
    ),
    url(
        r'^datastores/(?P<pk>[0-9a-zA-Z]{12})/?$',
        DatastoreDetail.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/properties/?$',
        DatastoreProperties.as_view(http_method_names=['get', 'post']),
    ),
]
