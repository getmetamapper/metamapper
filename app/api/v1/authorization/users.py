# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework import serializers

from app.api.v1.exceptions import NotFound
from app.api.v1.serializers import ApiSerializer
from app.api.v1.views import FindAPIView, ListAPIView, QueryParam

from app.authentication.models import User
from app.authorization.models import Membership


class UserSerializer(ApiSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'created_at',
        ]
        writable_fields = []


class MembershipSerializer(ApiSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            'id',
            'name',
            'email',
            'permissions',
            'created_at',
        ]
        writable_fields = []

    def get_id(self, obj):
        return obj.user.id

    def get_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email


class UserFind(FindAPIView):
    serializer_class = MembershipSerializer

    allowed_query_params = [
        QueryParam('email', required=True),
    ]

    def find_object(self, query_params):
        get_kwargs = {
            'user_id': query_params['email'].lower(),
            'workspace': self.request.workspace,
        }
        try:
            return Membership.objects.get(**get_kwargs)
        except Membership.DoesNotExist:
            raise NotFound()


class UserList(ListAPIView):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        return (
            self.request
                .workspace
                .memberships
                .prefetch_related('user')
                .order_by('created_at')
        )


urlpatterns = [
    url(
        r'^users/find/?$',
        UserFind.as_view(),
    ),
    url(
        r'^users/?$',
        UserList.as_view(),
    ),
]
