# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.authorization.users import UserSerializer
from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import FindAPIView, ListAPIView, QueryParam

from app.authorization.models import Group


class GroupSerializer(ApiSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'description',
            'created_at',
            'updated_at',
        ]
        writable_fields = []


class GroupFind(FindAPIView):
    serializer_class = GroupSerializer

    allowed_query_params = [
        QueryParam('name', required=True),
    ]

    def find_object(self, query_params):
        filter_kwargs = {
            'name__iexact': query_params['name'],
            'workspace': self.request.workspace,
        }
        return Group.objects.filter(**filter_kwargs).first()


class GroupList(ListAPIView):
    serializer_class = GroupSerializer

    def get_queryset(self):
        return Group.objects.filter(workspace=self.request.workspace)


class GroupUserList(ListAPIView):
    serializer_class = UserSerializer

    def get_object(self, pk):
        get_kwargs = {
            'workspace': self.request.workspace,
            'id': pk,
        }
        try:
            return Group.objects.get(**get_kwargs)
        except Group.DoesNotExist:
            raise NotFound()

    def get_queryset(self):
        return self.get_object(self.kwargs['pk']).user_set.order_by('fname')


urlpatterns = [
    url(
        r'^groups/find/?$',
        GroupFind.as_view(),
    ),
    url(
        r'^groups/?$',
        GroupList.as_view(),
    ),
    url(
        r'^groups/(?P<pk>[0-9]+)/users/?$',
        GroupUserList.as_view(),
    ),
]
