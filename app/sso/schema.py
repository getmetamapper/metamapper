# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.sso.models as models
import utils.connections as connections

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class SSOConnectionType(AuthNode, DjangoObjectType):
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    name = graphene.String()
    provider = graphene.String()
    protocol = graphene.String()
    audience = graphene.String()
    default_permissions = graphene.String()
    is_default = graphene.Boolean()

    extras = GenericScalar()
    mappings = GenericScalar()

    class Meta:
        model = models.SSOConnection
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_name(instance, info):
        return instance.name

    def resolve_protocol(instance, info):
        return instance.protocol

    def resolve_mappings(instance, info):
        return instance.extras.get("mappings", {})

    def resolve_audience(instance, info):
        return instance.audience

    def resolve_is_default(instance, info):
        return instance.id == info.context.workspace.active_sso_id


class SSODomainType(AuthNode, DjangoObjectType):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILURE = 'FAILURE'

    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    is_verified = graphene.Boolean()
    verification_status = graphene.String()

    class Meta:
        model = models.SSODomain
        filter_fields = []
        exclude_fields = ['verified_at', 'updated_at']
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection

    def resolve_is_verified(instance, info):
        return instance.verified

    def resolve_verification_status(instance, info):
        """Text representation of verification status.
        """
        if instance.verified:
            return SSODomainType.SUCCESS
        elif instance.verification_failed:
            return SSODomainType.FAILURE
        else:
            return SSODomainType.PENDING
