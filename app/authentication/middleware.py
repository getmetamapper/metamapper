# -*- coding: utf-8 -*-
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import ValidationError

from app.authentication.models import Workspace


def get_current_workspace(request):
    """Retrieve the current workspace based on the provider header value.
    """
    workspace = None
    pk = request.META.get('HTTP_X_WORKSPACE_ID')
    if pk:
        try:
            workspace = Workspace.objects.get(pk=pk)
        except (Workspace.DoesNotExist, ValidationError):
            pass
    return workspace


class CurrentWorkspaceMiddleware(object):
    def resolve(self, next, root, info, **args):
        """Attach the current workspace to the request.
        """
        info.context.workspace = get_current_workspace(info.context)
        return next(root, info, **args)
