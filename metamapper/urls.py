"""metamapper URL Configuration
"""
from django.conf.urls import url
from django.conf import settings
from django.urls import include

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def not_found(request):
    """Default "404 - not found" response for when routes are not defined.
    """
    return Response('404 - not found')


urlpatterns = [
    url(r'^', include(urlpattern)) for urlpattern in settings.URLPATTERNS
]

urlpatterns += [
    url(r'', not_found)
]
