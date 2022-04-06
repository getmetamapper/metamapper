# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import DetailAPIView, ListAPIView, QueryParam

from app.customfields.models import CustomField


class CustomFieldSerializer(ApiSerializer):
    related_type = serializers.CharField(
        source='content_type.name',
        read_only=True,
    )

    class Meta:
        model = CustomField
        fields = [
            'id',
            'related_type',
            'field_name',
            'field_type',
            'short_desc',
            'validators',
            'created_at',
            'updated_at',
        ]
        writable_fields = []


class CustomFieldList(ListAPIView):
    serializer_class = CustomFieldSerializer

    allowed_query_params = [
        QueryParam('related_type', required=True, choices=CustomField.SUPPORTED_MODELS),
    ]

    def get_queryset(self):
        query_params = self.parse_query_params(self.request)
        content_type = ContentType.objects.filter(model=query_params['related_type']).first()
        filter_kwargs = {
            'workspace': self.request.workspace,
            'content_type': content_type,
        }
        return CustomField.objects.filter(**filter_kwargs).prefetch_related('content_type')


class CustomFieldDetail(DetailAPIView):
    serializer_class = CustomFieldSerializer

    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'pk': pk,
        }
        try:
            return CustomField.objects.get(**get_kwargs)
        except CustomField.DoesNotExist:
            raise NotFound()


urlpatterns = [
    url(
        r'^properties/?$',
        CustomFieldList.as_view(),
    ),
    url(
        r'^properties/(?P<pk>[0-9a-zA-Z]{12})/?$',
        CustomFieldDetail.as_view(http_method_names=['get']),
    ),
]
