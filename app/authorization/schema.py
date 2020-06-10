# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authentication.models as models
import utils.connections as connections

from app.authorization.mixins import AuthNode
from app.authorization.permissions import AllowAuthenticated

from graphene_django import DjangoObjectType


class MembershipType(AuthNode, DjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    pk = graphene.Int()
    name = graphene.String()
    email = graphene.String()

    class Meta:
        model = models.Membership
        filter_fields = []
        exclude_fields = ('updated_at',)
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_pk(instance, info):
        try:
            return instance.user.pk
        except (AttributeError, models.User.DoesNotExist):
            return None

    def resolve_email(instance, info):
        return instance.user_id

    def resolve_name(instance, info):
        try:
            return instance.user.name
        except (AttributeError, models.User.DoesNotExist):
            return None
