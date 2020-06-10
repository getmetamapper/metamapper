"""metamapper URL Configuration
"""
from django.conf.urls import url
from django.urls import include, re_path

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from metamapper.views import (
    MetamapperGraphQLView,
    ReactAppView,
    StaticAssetView,
)

from app.sso.providers.oauth2.github.views import OAuth2GithubView
from app.sso.providers.oauth2.google.views import OAuth2GoogleView

from app.sso.providers.saml2.views import (
    SAML2AcceptACSView,
)


@api_view(['GET'])
def healthcheck(request):
    """Health check to see if server is up.
    """
    return Response({'status': 'ok'}, status=status.HTTP_200_OK)


urlpatterns = [
    re_path(
        r'^assets/(?P<filepath>.*)$',
        StaticAssetView.as_view(),
    ),
    url(r'^graphql/?$', MetamapperGraphQLView.as_view(graphiql=True)),
    url(
        r'^oauth2/',
        include(
            [
                url(
                    r'^github/callback/?$',
                    OAuth2GithubView.as_view(),
                    name="sso-oauth2-github",
                ),
                url(
                    r'^google/callback/?$',
                    OAuth2GoogleView.as_view(),
                    name="sso-oauth2-google",
                ),
            ]
        ),
    ),
    url(
        r'^saml2/',
        include(
            [
                url(
                    r'^acs/callback/?$',
                    SAML2AcceptACSView.as_view(),
                    name="sso-saml-acs",
                ),
            ]
        ),
    ),
    url(r'^health/?$', healthcheck),
    url(r'^', ReactAppView.as_view()),
]
