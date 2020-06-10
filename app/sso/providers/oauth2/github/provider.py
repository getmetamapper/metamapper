# -*- coding: utf-8 -*-
from base64 import b64encode
from rest_framework.reverse import reverse
from urllib.parse import urlencode

from app.sso.providers.oauth2.provider import OAuth2Provider
from app.sso.providers.oauth2.github import constants


class GithubOAuth2Provider(OAuth2Provider):
    """docstring for GithubOAuth2Provider
    """
    def build_identity(self, raw_attributes):
        """Return a mapping containing the identity information:
        {
            "ident", "email", "fname", "lname",
        }
        """
        return {
            "ident": raw_attributes["id"],
            "email": raw_attributes["email"],
            "fname": "",
            "lname": "",
            "email_verified": raw_attributes["verified"],
        }

    def get_client_id(self):
        """Get `CLIENT_ID` for easier mocking.
        """
        return constants.CLIENT_ID

    def get_redirect_url(self, request):
        """Build the redirection URL based on the connection and web request.
        """
        state = b64encode("connection={0}".format(self.connection.pk).encode()).decode('utf-8')
        redirect_uri = self.get_redirect_uri(request)
        redirect_uri = '{0}?state={1}'.format(redirect_uri, state)
        state_kwargs = {
            'client_id': self.get_client_id(),
            'scope': constants.SCOPE,
            'redirect_uri': redirect_uri,
        }
        return constants.AUTHORIZE_URL + '?' + urlencode(state_kwargs)

    def get_redirect_uri(self, request):
        """Get the proper redirect URI for Github.
        """
        return reverse("sso-oauth2-github", request=request)
