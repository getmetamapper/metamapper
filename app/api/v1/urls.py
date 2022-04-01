# -*- coding: utf-8 -*-
from django.conf.urls import url

from app.api.v1 import definitions


urlpatterns = [
    url(
        r'^test/?$',
        definitions.example_view,
        name='test'
    ),
]
