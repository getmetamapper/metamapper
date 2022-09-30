# -*- coding: utf-8 -*-
import graphene.relay as relay

import app.api.models as models
import utils.connections as connections

from graphene_django import DjangoObjectType

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class ApiTokenType(AuthNode, DjangoObjectType):
    """GraphQL representation of an API token.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    class Meta:
        model = models.ApiToken
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'id',
            'name',
            'is_enabled',
            'created_at',
            'updated_at',
        )

    @classmethod
    def get_node(cls, info, id):
        """We should only return tables related to the current workspace.
        """
        return models.ApiToken.objects.filter(
            workspace=info.context.workspace,
            id=id,
        ).first()
