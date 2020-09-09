# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.revisioner.models as models
import utils.connections as connections

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class RevisionerErrorType(AuthNode, DjangoObjectType):
    """GraphQL representation of an error in a Revisioner run.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    class Meta:
        model = models.RevisionerError
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = ['exc_message']


class RunType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Revisioner run.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    status = graphene.String()

    created_on = graphene.Date()

    error = graphene.Field(RevisionerErrorType)

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

    def resolve_error(instance, info):
        """Return the first error associated with this run, if any exist.
        """
        return instance.errors.order_by('created_at').first()

    def resolve_created_on(instance, info):
        """Return the `created_at` timestamp as a date.
        """
        return instance.created_at.date()


class RelatedResourceType(graphene.ObjectType):
    """Generic type for all Revisable models.
    """
    id = graphene.ID()
    type = graphene.String()
    name = graphene.String()
    label = graphene.String()
    pathname = graphene.String()
    parent_label = graphene.String()


class RevisionType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Revision.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    metadata = GenericScalar()
    parent_resource = graphene.Field(RelatedResourceType)
    related_resource = graphene.Field(RelatedResourceType)

    class Meta:
        model = models.Revision
        filter_fields = []
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = []

    def resolve_related_resource(instance, info):
        """Return the resource related to this Revision.
        """
        return info.context.loaders.related_revision_resources.load(instance.revision_id)

    def resolve_parent_resource(instance, info):
        """Return the resource related to this Revision.
        """
        if not instance.parent_resource_revision_id:
            return None
        return info.context.loaders.related_revision_resources.load(instance.parent_resource_revision_id)
