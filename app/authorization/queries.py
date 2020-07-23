# -*- coding: utf-8 -*-
import graphene
import graphql_relay

import utils.errors as errors
import utils.shortcuts as shortcuts

from app.authentication.schema import UserType
from app.authorization.schema import GroupType, MembershipType

from app.authorization.models import Group, Membership

from app.authorization.fields import AuthConnectionField
from app.authorization import permissions as auth_perms


class Query(graphene.ObjectType):
    """Queries related to the authentication models.
    """
    workspace_users = AuthConnectionField(
        type=MembershipType,
        workspace_id=graphene.ID(required=True),
        permissions=graphene.List(graphene.String, required=False),
        active_only=graphene.Boolean(required=False),
    )

    workspace_groups = AuthConnectionField(
        type=GroupType,
    )

    workspace_group = graphene.Field(
        type=GroupType,
        id=graphene.ID(required=True),
    )

    workspace_group_users = AuthConnectionField(
        type=UserType,
        group_id=graphene.ID(required=True),
    )

    @auth_perms.login_required
    def resolve_workspace_users(self, info, workspace_id, permissions=None, active_only=False):
        """Retrieve team members of a Workspace that the current user belongs to.
        """
        _type, node_id = graphql_relay.from_global_id(workspace_id)

        if not info.context.user.permissions_for(node_id):
            raise errors.PermissionDenied()

        queryset = Membership.objects.filter(workspace_id=node_id)

        if permissions:
            queryset = queryset.filter(permissions__in=permissions)

        if active_only:
            queryset = queryset.filter(user__id__isnull=False)

        return queryset.distinct()

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_workspace_groups(self, info, *args, **kwargs):
        """Retrieve all groups associated with the workspace.
        """
        return info.context.workspace.groups.order_by('name')

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_workspace_group(self, info, id):
        """Retrieve a group by the ID. Scoped to the current workspace.
        """
        _type, pk = shortcuts.from_global_id(id)
        get_kwargs = {
            'workspace_id': info.context.workspace.pk,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(Group, **get_kwargs)

    @auth_perms.permissions_required((auth_perms.WorkspaceTeamMembersOnly,))
    def resolve_workspace_group_users(self, info, group_id):
        """Retrieve the users of the provided group. Scoped to the current workspace.
        """
        _type, pk = shortcuts.from_global_id(group_id)
        get_kwargs = {
            'workspace_id': info.context.workspace.pk,
            'pk': pk,
        }
        return shortcuts.get_object_or_404(Group, **get_kwargs).user_set.order_by('fname')
