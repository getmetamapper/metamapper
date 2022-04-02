# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.api.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_properties(request, format=None):
    """GET /api/v1/properties
    """
    content = {
        'status': 'request was permitted'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_property(request, format=None):
    """GET /api/v1/properties/:id
    """
    content = {
        'status': 'request was permitted'
    }
    return Response(content)
