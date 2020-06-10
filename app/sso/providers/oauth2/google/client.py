# -*- coding: utf-8 -*-
import datetime as dt
import requests

from django.conf import settings
from django.utils import timezone

from app.sso.providers.oauth2.google import constants


class GoogleApiError(Exception):
    """Custom error message for Google API.
    """
    def __init__(self, message="", status=0):
        super(GoogleApiError, self).__init__(message)
        self.status = status


class GoogleClient(object):
    """Access the Google API with this client.
    """
    def __init__(self, refresh_token=None):
        self.client_id = constants.CLIENT_ID
        self.client_secret = constants.CLIENT_SECRET
        self.http = requests.Session()
        self.refresh_token = refresh_token
        self.access_token = None
        self.issued_at = None

    def get_default_params(self, **extras):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        params.update(**extras)
        return params

    @property
    def token_expired(self):
        return (
            self.issued_at is None or self.issued_at < (timezone.now() - dt.timedelta(minutes=50))
        )

    def get_or_refresh_access_token(self):
        """Exactly what it sounds like.
        """
        if not self.access_token or self.token_expired:
            self.access_token = self.get_access_token()
            self.issued_at = timezone.now()
        return self.access_token

    def get_access_token(self):
        """Fetch the access token.
        """
        req = self.http.post(
            url=constants.REFRESH_TOKEN_URL,
            params=self.get_default_params(
                refresh_token=self.refresh_token,
                grant_type="refresh_token",
            ),
        )

        if req.status_code < 200 or req.status_code >= 300:
            raise GoogleApiError(req.content, status=req.status_code)

        return req.json().get('access_token')

    def set_access_token(self, code):
        """Get the initial access token.
        """
        req = self.http.post(
            url=constants.ACCESS_TOKEN_URL,
            params=self.get_default_params(
                code=code,
                grant_type="authorization_code",
                redirect_uri="{0}/oauth2/google/callback".format(settings.GRAPHQL_ORIGIN),
            ),
        )

        if req.status_code < 200 or req.status_code >= 300:
            raise GoogleApiError(req.content, status=req.status_code)

        params = req.json()

        self.access_token = params.get('access_token')
        self.issued_at = timezone.now()
        self.refresh_token = params.get('refresh_token')

    def _http_request(self, path, **params):
        """Helper function to hit the Google API.
        """
        tok = self.get_or_refresh_access_token()
        req = self.http.get(
            url="https://www.{0}/{1}".format(constants.API_DOMAIN, path.lstrip("/")),
            params=params,
            headers={
                "Authorization": "Bearer {0}".format(tok)
            }
        )
        if req.status_code < 200 or req.status_code >= 300:
            raise GoogleApiError(req.content, status=req.status_code)
        return req.json()

    def get_user(self):
        """Get information about the current user.
        """
        return self._http_request("oauth2/v3/userinfo", alt="json")

    def get_user_domain(self):
        """Get the domain for the current user.
        """
        domain = None
        user = self.get_user()
        if user:
            domain = user.get("email", "").split("@")[1]
        return domain.lower()
