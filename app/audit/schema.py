# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.audit.models as models

import utils.connections as connections
import utils.shortcuts as shortcuts

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class AuditActivityActionObjectType(graphene.ObjectType):
    """The affected object of the action.
    """
    id = graphene.ID()
    pk = graphene.String()

    display_name = graphene.String()
    object_type = graphene.String()

    def resolve_id(instance, info):
        """Get the global ID for the object.
        """
        return shortcuts.to_global_id('%sType' % instance.__class__.__name__, instance.id)

    def resolve_object_type(instance, info):
        """The type of object being returned.
        """
        return instance.__class__.__name__

    def resolve_display_name(instance, info):
        """Special `displayName` for the UI.
        """
        return instance.display_name if hasattr(instance, 'display_name') else None



class AuditActivityTargetType(graphene.ObjectType):
    """The primary target of the action.
    """
    id = graphene.ID()
    pk = graphene.String()

    display_name = graphene.String()
    object_type = graphene.String()

    parent_resource = graphene.Field(
        'app.audit.schema.AuditActivityTargetType'
    )

    def resolve_id(instance, info):
        """Get the global ID for the object.
        """
        return shortcuts.to_global_id('%sType' % instance.__class__.__name__, instance.id)

    def resolve_object_type(instance, info):
        """The type of object being returned.
        """
        return instance.__class__.__name__

    def resolve_display_name(instance, info):
        """Special `displayName` for the UI.
        """
        return instance.display_name

    def resolve_parent_resource(instance, info):
        """Parent resource. For a Table, this would be a Schema.
        """
        return instance.parent_resource


class AuditActivityType(AuthNode, DjangoObjectType):
    """GraphQL representation of a `audit.Activity` instance.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    action_object = graphene.Field(AuditActivityActionObjectType)
    target = graphene.Field(AuditActivityTargetType)

    old_values = graphene.Field(GenericScalar)
    new_values = graphene.Field(GenericScalar)

    class Meta:
        model = models.Activity
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'action_object',
            'actor',
            'target',
            'timestamp',
            'old_values',
            'new_values',
            'verb',
        )
