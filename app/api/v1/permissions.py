# -*- coding: utf-8 -*-
from rest_framework import permissions

from app.api.v1.exceptions import PermissionDenied


class IsAuthenticated(permissions.BasePermission):
    """Standard authentication scheme for the API integration.
    """
    def has_permission(self, request, view):
        """Check if the request is authenticated.
        """
        if not request.workspace or not request.api_token:
            raise PermissionDenied()

        return True
