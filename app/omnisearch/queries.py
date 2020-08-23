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
        datastore_id=graphene.String(required=False),
    )

    @permissions.permissions_required(permission_classes=(permissions.WorkspaceTeamMembersOnly,))
    def resolve_omnisearch(self, info, content, datastore_id=None, **kwargs):
        """Execute a search query and return a result.
        """
        filter_kwargs = {
            'search_query_string': content,
            'workspace': info.context.workspace,
        }

        if datastore_id:
            filter_kwargs['datastore_id'] = datastore_id

        start_t = time.time()
        results = get_search_backend(info.context.workspace, info.context.user).search(**filter_kwargs)

        return dict(search_results=results, time_elapsed=round(time.time() - start_t, 3))
