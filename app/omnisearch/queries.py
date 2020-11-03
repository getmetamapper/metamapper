# -*- coding: utf-8 -*-
import graphene
import time

from app.omnisearch import schema
from app.omnisearch.backends import get_search_backend

from app.authorization import permissions


class Query(graphene.ObjectType):
    """Queries related to the definitions models.
    """
    omnisearch = graphene.Field(
        schema.OmnisearchResponseType,
        content=graphene.String(required=True),
        types=graphene.List(graphene.String, required=False),
        datastores=graphene.List(graphene.String, required=False),
        engines=graphene.List(graphene.String, required=False),
        schemas=graphene.List(graphene.String, required=False),
        tags=graphene.List(graphene.String, required=False),
    )

    @permissions.permissions_required(permission_classes=(permissions.WorkspaceTeamMembersOnly,))
    def resolve_omnisearch(self, info, content, **extras):
        """Execute a search query and return a result.
        """
        omnisearch = get_search_backend(info.context.workspace, info.context.user)
        omnisearch.execute(content, **extras)
        return omnisearch.to_dict()
