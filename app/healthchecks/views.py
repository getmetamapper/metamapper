# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def healthcheck(request):
    """Check to see if certain Metamapper services are healthy.

    Example Response:

    {
        "metastore": {
            "status": "healthly"
        },
        "scheduler": {
            "status": "healthy",
            "latest_scheduler_heartbeat": "2020-07-21 05:23:19+00:00"
        },
        "worker": {
            "status": "healthly"
        }
    }
    """
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)
