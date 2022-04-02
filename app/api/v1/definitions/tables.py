# -*- coding: utf-8 -*-
from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import DetailAPIView, FindAPIView, ListAPIView
from app.definitions.models import Table


class TableSerializer(ApiSerializer):
    id = serializers.SerializerMethodField()

    tags = serializers.ListField(
        child=serializers.CharField(max_length=30),
        max_length=10,
        allow_empty=True,
        allow_null=True,
        required=False,
    )

    class Meta:
        model = Table
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


class TableList(ListAPIView):
    serializer_class = TableSerializer

    def get_queryset(self):
        filter_kwargs = {
            'schema_id': self.kwargs['schema_id'],
            'workspace': self.request.workspace,
        }
        return Table.objects.filter(**filter_kwargs)


class TableDetail(DetailAPIView):
    serializer_class = TableSerializer

    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'object_id': pk,
        }
        try:
            return Table.objects.get(**get_kwargs)
        except Table.DoesNotExist:
            raise NotFound()


class TableFind(FindAPIView):
    serializer_class = TableSerializer

    required_query_params = ['schema', 'name']

    def find_object(self, datastore_id, query_params):
        filter_kwargs = {
            'workspace': self.request.workspace,
            'schema__datastore_id': datastore_id,
            'schema__name': query_params['schema'],
            'name': query_params['name'],
        }
        return Table.objects.filter(**filter_kwargs).first()
