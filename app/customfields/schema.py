# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.customfields.models as models

import utils.connections as connections

from graphene_django import DjangoObjectType
from graphene.types.generic import GenericScalar

from app.authorization.mixins import AuthNode
from app.authorization.permissions import WorkspaceTeamMembersOnly


class CustomFieldType(AuthNode, DjangoObjectType):
    """GraphQL representation of a CustomField.
    """
    permission_classes = (WorkspaceTeamMembersOnly,)
    scope_to_workspace = True

    validators = graphene.Field(GenericScalar)

    class Meta:
        model = models.CustomField
        filter_fields = {}
        interfaces = (relay.Node,)
        connection_class = connections.DefaultConnection
        only_fields = (
            'id',
            'pk',
            'field_name',
            'field_type',
            'validators',
            'short_desc',
            'created_at',
            'updated_at',
        )
