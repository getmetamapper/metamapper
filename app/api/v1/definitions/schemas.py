# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import DetailAPIView, FindAPIView, ListAPIView, QueryParam

from app.definitions.models import Schema

from utils.fields import SortedListField


class SchemaSerializer(ApiSerializer):
    id = serializers.SerializerMethodField()

    tags = SortedListField(
        child=serializers.CharField(max_length=30),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Schema
        fields = [
            'id',
            'name',
            'tags',
            'created_at',
            'updated_at',
        ]
        writable_fields = ['tags']

    def get_id(self, obj):
        return obj.object_id

    def validate_tags(self, tags):
        return list(set(tags)) if isinstance(tags, (list,)) else []

    def update(self, instance, validated_data):
        instance.tags = validated_data.get('tags', instance.tags)
        instance.save()
        return instance


class SchemaList(ListAPIView):
    serializer_class = SchemaSerializer

    def get_queryset(self):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'datastore_id': self.kwargs['datastore_id'],
        }
        return Schema.objects.filter(**filter_kwargs)


class SchemaDetail(DetailAPIView):
    serializer_class = SchemaSerializer

    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'object_id': pk,
        }
        try:
            return Schema.objects.get(**get_kwargs)
        except Schema.DoesNotExist:
            raise NotFound()


class SchemaFind(FindAPIView):
    serializer_class = SchemaSerializer

    allowed_query_params = [
        QueryParam('name', required=True),
    ]

    def find_object(self, datastore_id, query_params):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'datastore_id': datastore_id,
            'name': query_params['name'],
        }
        return Schema.objects.filter(**filter_kwargs).first()


urlpatterns = [
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/schemas/find/?$',
        SchemaFind.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/schemas/?$',
        SchemaList.as_view(),
    ),
    url(
        r'^schemas/(?P<pk>[a-f0-9]{32})/?$',
        SchemaDetail.as_view(),
    ),
]
