# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.urls import include

from rest_framework.decorators import api_view
from rest_framework.response import Response

from app.api.v1.exceptions import NotFound

from app.api.v1.customfields import properties

from app.api.v1.definitions import datastores
from app.api.v1.definitions import schemas
from app.api.v1.definitions import tables
from app.api.v1.definitions import columns


@api_view(['GET'])
def not_found(request, format=None):
    """Default "404 - Not Found" response for when routes are not defined.
    """
    raise NotFound()


@api_view(['GET'])
def healthcheck(request):
    """Check to see if API is healthy.
    """
    return Response({'success': True})


baseurls = [
    url(r'^health/?$', healthcheck),
    url(r'', not_found)
]

api = [
    *datastores.urlpatterns,
    *schemas.urlpatterns,
    *tables.urlpatterns,
    *columns.urlpatterns,
    *properties.urlpatterns,
    *baseurls,
]


urlpatterns = [
    url(r'^api/v1/', include(api)),
]
