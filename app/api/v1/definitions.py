# -*- coding: utf-8 -*-
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from app.api.permissions import IsAuthenticated


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def example_view(request, format=None):
    content = {
        'status': 'request was permitted'
    }
    return Response(content)
