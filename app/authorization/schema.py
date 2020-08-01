# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import utils.connections as connections

from app.authorization.mixins import AuthNode
from app.authorization.permissions import AllowAuthenticated, WorkspaceTeamMembersOnly

from app.authentication.models import User, Group
from app.authorization.models import Membership

from graphene_django import DjangoObjectType
from graphql_relay import to_global_id


class MembershipType(AuthNode, DjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    user_id = graphene.ID()
    pk = graphene.Int()
    name = graphene.String()
    email = graphene.String()

    class Meta:
        model = Membership
        filter_fields = []
        exclude_fields = ('updated_at',)
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_user_id(instance, info):
        try:
            return to_global_id('UserType', instance.user.pk)
        except (AttributeError, User.DoesNotExist):
            return None

    def resolve_pk(instance, info):
        try:
            return instance.user.pk
        except (AttributeError, User.DoesNotExist):
            return None

    def resolve_email(instance, info):
        return instance.user_id

    def resolve_name(instance, info):
        try:
            return instance.user.name
        except (AttributeError, User.DoesNotExist):
            return None


class GroupType(AuthNode, DjangoObjectType):
    permission_classes = (WorkspaceTeamMembersOnly,)

    pk = graphene.Int()

    users_count = graphene.Int()

    class Meta:
        model = Group
        filter_fields = []
        exclude_fields = []
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_pk(instance, info):
        return instance.id

    def resolve_users_count(instance, info):
        """TODO(scruwys): Move this to a loader.
        """
        return instance.user_set.count()
