# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.revisioner.models as models
import utils.connections as connections

from graphene_django import DjangoObjectType

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class RunType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Revisioner run.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    status = graphene.String()

    created_on = graphene.Date()

    class Meta:
        model = models.Run
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    def resolve_status(instance, info):
        """The current status of the run.
        """
        return instance.status

    def resolve_created_on(instance, info):
        """Return the `created_at` timestamp as a date.
        """
        return instance.created_at.date()
