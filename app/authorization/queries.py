# -*- coding: utf-8 -*-
import graphene
import graphql_relay

import app.authorization.models as models
import app.authorization.schema as schema

from app.authorization.permissions import login_required

from app.authorization.fields import AuthConnectionField
from utils.errors import PermissionDeniedError


class Query(graphene.ObjectType):
    """Queries related to the authentication models.
    """
    workspace_users = AuthConnectionField(
        type=schema.MembershipType,
        workspace_id=graphene.ID(required=True),
        permissions=graphene.List(graphene.String, required=False),
        active_only=graphene.Boolean(required=False),
    )

    @login_required
    def resolve_workspace_users(self, info, workspace_id, permissions=None, active_only=False):
        """Retrieve team members of a Workspace that the current user belongs to.
        """
        _type, node_id = graphql_relay.from_global_id(workspace_id)

        if not info.context.user.permissions_for(node_id):
            raise PermissionDeniedError()

        queryset = models.Membership.objects.filter(workspace_id=node_id)

        if permissions:
            queryset = queryset.filter(permissions__in=permissions)

        if active_only:
            queryset = queryset.filter(user__id__isnull=False)

        return queryset.distinct()
