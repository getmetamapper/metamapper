# -*- coding: utf-8 -*-
from django.conf.urls import url

from rest_framework.decorators import api_view

from app.api.v1.exceptions import NotFound

from app.api.v1.definitions import datastores
from app.api.v1.definitions import schemas
from app.api.v1.definitions import tables
from app.api.v1.definitions import columns


@api_view(['GET'])
def not_found(request, format=None):
    """Default "404 - Not Found" response for when routes are not defined.
    """
    raise NotFound()


urlpatterns = [
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/schemas/find/?$',
        schemas.SchemaFind.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/schemas/?$',
        schemas.SchemaList.as_view(),
    ),
    url(
        r'^schemas/(?P<pk>[a-f0-9]{32})/?$',
        schemas.SchemaDetail.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/tables/find/?$',
        tables.TableFind.as_view(),
    ),
    url(
        r'^schemas/(?P<schema_id>[a-f0-9]{32})/tables/?$',
        tables.TableList.as_view(),
    ),
    url(
        r'^tables/(?P<pk>[a-f0-9]{32})/?$',
        tables.TableDetail.as_view(),
    ),
    url(
        r'^datastores/(?P<datastore_id>[0-9a-zA-Z]{12})/columns/find/?$',
        columns.ColumnFind.as_view(),
    ),
    url(
        r'^tables/(?P<table_id>[a-f0-9]{32})/columns/?$',
        columns.ColumnList.as_view(),
    ),
    url(
        r'^columns/(?P<pk>[a-f0-9]{32})/?$',
        columns.ColumnDetail.as_view(),
    ),
    url(r'', not_found),
]
