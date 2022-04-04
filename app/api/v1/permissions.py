# -*- coding: utf-8 -*-
from rest_framework import permissions

from app.api.v1.exceptions import PermissionDenied


class IsAuthenticated(permissions.BasePermission):
    """Standard authentication scheme for the API integration.
    """
    def has_permission(self, request, view):
        """Check if the request is authenticated.
        """
        if not request.workspace:
            raise PermissionDenied()

        if not request.api_token or not request.api_token.is_enabled:
            raise PermissionDenied()

        return True
