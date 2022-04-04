# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework.decorators import api_view

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


baseurls = [
    url(r'', not_found)
]

urlpatterns = [
    *datastores.urlpatterns,
    *schemas.urlpatterns,
    *tables.urlpatterns,
    *columns.urlpatterns,
    *properties.urlpatterns,
    *baseurls,
]
