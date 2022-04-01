# -*- coding: utf-8 -*-
from base64 import b64decode
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

from app.api.models import ApiToken
from app.authentication.models import Workspace


class IsAuthenticated(permissions.BasePermission):
    """Standard authentication scheme for the API integration.
    """
    def has_permission(self, request, view):
        """Check if the request is authenticated.
        """
        workspace = self.get_workspace(request)

        if not workspace:
            raise PermissionDenied(detail='Invalid credentials')

        api_token = self.get_api_token(request, workspace)

        if not api_token:
            raise PermissionDenied(detail='Invalid credentials')

        return True

    def get_workspace(self, request):
        """Retrieve the Workspace from the headers.
        """
        workspace_id = request.META.get('HTTP_X_WORKSPACE_ID')

        if not workspace_id:
            return None

        return Workspace.objects.filter(id=workspace_id).first()

    def get_api_token(self, request, workspace):
        """Retrieve the ApiToken from the headers.
        """
        authorization = request.META.get('HTTP_AUTHORIZATION')

        if not authorization:
            return None

        secret = ''.join(authorization.split()[1:])
        token_parts = b64decode(secret.encode()).decode().split(':')

        if len(token_parts) != 2:
            return None

        api_token = ApiToken.objects.filter(
            id=token_parts[0],
            workspace_id=workspace.id,
        ).first()

        if api_token and api_token.token == token_parts[1]:
            return api_token
