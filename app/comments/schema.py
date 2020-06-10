# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.comments.models as models
import utils.connections as connections

from graphene_django import DjangoObjectType

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class CommentType(AuthNode, DjangoObjectType):
    """GraphQL representation of a Comment.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    child_comments = graphene.List('app.comments.schema.CommentType')
    is_pinned = graphene.Boolean()

    class Meta:
        model = models.Comment
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        exclude_fields = ()

    def resolve_child_comments(instance, info):
        """Returns the children comments if any exist.
        """
        return info.context.loaders.child_comments.load(instance.pk)

    def resolve_is_pinned(instance, info):
        """Boolean indicator if we pinned a comment.
        """
        return instance.pinned_at is not None
