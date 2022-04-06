"""metamapper URL Configuration
"""
from django.conf.urls import url

from django.urls import include, re_path

from metamapper.views import (
    MetamapperGraphQLView,
    ReactAppView,
    StaticAssetView,
)

from app.healthchecks.views import healthcheck

from app.sso.providers.oauth2.github.views import OAuth2GithubView
from app.sso.providers.oauth2.google.views import OAuth2GoogleView
from app.sso.providers.saml2.views import SAML2AcceptACSView


urlpatterns = [
    re_path(
        r'^assets/(?P<filepath>.*)$',
        StaticAssetView.as_view(),
    ),
    url(
        r'^graphql/?$',
        MetamapperGraphQLView.as_view(graphiql=True),
    ),
    url(
        r'^oauth2/',
        include(
            [
                url(
                    r'^github/callback/?$',
                    OAuth2GithubView.as_view(),
                    name='sso-oauth2-github',
                ),
                url(
                    r'^google/callback/?$',
                    OAuth2GoogleView.as_view(),
                    name='sso-oauth2-google',
                ),
            ],
        ),
    ),
    url(
        r'^saml2/',
        include(
            [
                url(
                    r'^acs/callback/?$',
                    SAML2AcceptACSView.as_view(),
                    name='sso-saml-acs',
                ),
            ],
        ),
    ),
    url(r'^health/?$', healthcheck, name='healthcheck'),
    url(r'^', ReactAppView.as_view()),
]
