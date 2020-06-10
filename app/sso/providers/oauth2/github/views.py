# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseRedirect

from app.authentication.models import User

from rest_framework.views import APIView
from app.sso.providers.views import SSOViewMixin

from app.sso.providers.constants import ERR_SSO_NOT_ENABLED
from app.sso.providers.oauth2.github.provider import GithubOAuth2Provider
from app.sso.providers.oauth2.github.client import GithubClient
from app.sso.providers.oauth2.provider import (
    build_oauth_config,
    is_login_flow,
    prepare_auth_request,
)


class OAuth2GithubView(SSOViewMixin, APIView):
    """Process Github OAuth2 authentication request via callback function.
    """
    def dispatch(self, request, *args, **kwargs):
        """The SAML2.0 request should immediately attempt to login.
        """
        auth = prepare_auth_request(request)

        client = GithubClient()
        client.set_access_token(auth["get_data"]["code"])

        if is_login_flow(auth["get_data"]["state"]):
            return self.login_pipeline(request, client)
        else:
            return self.setup_pipeline(request, client)

    def get_provider(self, *args, **kwargs):
        """Helper function for grabbing the provider class.
        """
        return GithubOAuth2Provider(*args, **kwargs)

    def build_state_from_request(self, request, client):
        """Create state for the request.
        """
        state = {}
        error = None

        auth = prepare_auth_request(request)
        config = build_oauth_config(auth["get_data"]["state"])

        connection = self.get_sso_connection(config["connection"])

        if not connection:
            return (connection, state, ERR_SSO_NOT_ENABLED)

        if not client.is_org_member(connection.entity_id):
            error = "You are not an authorized member of the connected GitHub organization."

        state = client.get_user()

        for email in client.get_user_emails():
            if email["primary"]:
                state.update(**email)

        return (connection, state, error)

    def setup_pipeline(self, request, client, *args, **kwargs):
        """Initiate the setup pipeline.
        """
        auth = prepare_auth_request(request)
        state = build_oauth_config(auth["get_data"]["state"])

        user = User.objects.get(id=state["uid"])
        user.set_github_oauth2_token(client.access_token)
        user.save()

        redirect_to = (
            '{0}/{1}/settings/authentication/setup/github'.format(
                settings.WEBSERVER_ORIGIN,
                state["wksp"],
            )
        )

        return HttpResponseRedirect(redirect_to)
