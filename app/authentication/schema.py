# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authentication.models as models
import utils.connections as connections

from app.authorization.mixins import AuthNode
from app.authorization.permissions import AllowAuthenticated
from app.authorization.schema import MembershipType

from graphene_django import DjangoObjectType


class UserType(AuthNode, DjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    pk = graphene.Int()
    name = graphene.String()
    avatar_url = graphene.String()

    current_membership = graphene.Field(MembershipType)
    is_current_user = graphene.Boolean()

    class Meta:
        model = models.User
        filter_fields = []
        exclude_fields = (
            'password',
            'sso_access_token',
            'sso_access_token_issued_at',
            'github_oauth2_token',
            'github_oauth2_token_issued_at',
            'google_oauth2_token',
            'google_oauth2_token_issued_at',
        )
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_pk(instance, info):
        """Return the id of the current user.
        """
        return instance.id

    def resolve_avatar_url(instance, info):
        return instance.avatar_url

    def resolve_current_membership(instance, info):
        """Resolve the current membership, if applicable.
        """
        if not info.context.user == instance:
            return None

        if not hasattr(info.context, 'workspace') or not info.context.workspace:
            return None

        return instance.memberships.filter(workspace_id=info.context.workspace.id).first()

    def resolve_name(instance, info):
        return instance.name

    def resolve_is_current_user(instance, info):
        """Boolean indicator if this is the current user.
        """
        return info.context.user == instance


class WorkspaceType(AuthNode, DjangoObjectType):
    permission_classes = (AllowAuthenticated,)

    class Meta:
        model = models.Workspace
        exclude_fields = ('ssh_private_key', 'created_at', 'updated_at',)
        filter_fields = {
            'name': ['exact', 'icontains', 'istartswith'],
        }
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    @classmethod
    def get_node(cls, info, pk):
        return info.context.user.workspaces.filter(pk=pk).first()
