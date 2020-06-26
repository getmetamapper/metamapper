# -*- coding: utf-8 -*-
import graphene
import graphene.relay as relay

import app.authentication.models as models
import app.authentication.schema as schema

from app.authorization.fields import AuthConnectionField
from app.authorization.permissions import login_required


class Query(graphene.ObjectType):
    """Queries related to the authentication models.
    """
    me = graphene.Field(schema.UserType)

    workspace = relay.Node.Field(schema.WorkspaceType)

    my_workspaces = AuthConnectionField(schema.WorkspaceType)

    workspace_by_slug = graphene.Field(
        type=schema.WorkspaceType,
        slug=graphene.String(required=True),
    )

    initiate_setup_process = graphene.Field(graphene.Boolean)

    @login_required
    def resolve_me(self, info, **kwargs):
        """Retrieve the current user.
        """
        return info.context.user

    @login_required
    def resolve_my_workspaces(self, info, **kwargs):
        """Retrieve the Workspace objects that the current user belongs to.
        """
        return info.context.user.workspaces.filter(**kwargs).order_by('name')

    @login_required
    def resolve_workspace_by_slug(self, info, slug):
        """Retrieve any workspace by slug.
        """
        return info.context.user.workspaces.filter(slug__iexact=slug.lower()).first()

    def resolve_initiate_setup_process(self, info, **kwargs):
        """Check to see if Metamapper has been set up.
        """
        return models.User.objects.first() is None
