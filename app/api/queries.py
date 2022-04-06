# -*- coding: utf-8 -*-
import graphene

from app.api.schema import ApiTokenType

from app.authorization.fields import AuthConnectionField
from app.authorization import permissions as auth_perms


class Query(graphene.ObjectType):
    """Queries related to the api models.
    """
    api_tokens = AuthConnectionField(ApiTokenType)

    @auth_perms.permissions_required((auth_perms.WorkspaceOwnersOnly,))
    def resolve_api_tokens(self, info, *args, **kwargs):
        """Retrieve the API tokens associated with this workspace.
        """
        return info.context.workspace.api_tokens.order_by('created_at')
