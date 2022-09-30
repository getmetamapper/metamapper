# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.integrations.models as models
import app.integrations.registry as registry

import utils.connections as connections

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authentication.schema import UserType
from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class IntegrationFieldType(graphene.ObjectType):
    """GraphQL representation of the fields on a dynamic option class.
    """
    label = graphene.String()
    name = graphene.String()
    type = graphene.String()
    options = GenericScalar()
    help_text = graphene.String()
    is_display = graphene.Boolean()
    is_required = graphene.Boolean()


class IntegrationType(graphene.ObjectType):
    """GraphQL representation of an dynamic option class.
    """
    name = graphene.String()
    info = graphene.String()

    handler = graphene.String()
    details = graphene.List(IntegrationFieldType)

    installed = graphene.Boolean()
    tags = graphene.List(graphene.String)


class IntegrationConfigType(AuthNode, DjangoObjectType):
    """GraphQL representation of an integration configuration.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    created_by = graphene.Field(UserType)
    auth_keys = graphene.List(graphene.String)
    meta = graphene.Field(GenericScalar)

    class Meta:
        model = models.IntegrationConfig
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'id',
            'auth_keys',
            'displayable',
            'integration',
            'meta',
            'created_by',
            'created_at',
            'updated_at',
        )

    @classmethod
    def get_node(cls, info, id):
        """We should only return tables related to the current workspace.
        """
        return models.IntegrationConfig.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()

    def resolve_created_by(instance, info):
        return info.context.loaders.users.load(instance.user_id)

    def resolve_auth_keys(instance, info):
        return registry.find_integration(instance.integration).handler.Meta.auth_keys
