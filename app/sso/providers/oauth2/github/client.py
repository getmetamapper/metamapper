# -*- coding: utf-8 -*-
import requests
import six
import urllib.parse as parse

from app.sso.providers.oauth2.github import constants


class GitHubApiError(Exception):
    """Custom error message for GitHub API.
    """
    def __init__(self, message="", status=0):
        super(GitHubApiError, self).__init__(message)
        self.status = status


class GithubClient(object):
    """Access the Github API with this client.
    """
    def __init__(self, access_token=None):
        self.client_id = constants.CLIENT_ID
        self.client_secret = constants.CLIENT_SECRET
        self.http = requests.Session()
        self.access_token = access_token

    def get_default_params(self, **extras):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        params.update(**extras)
        return params

    def set_access_token(self, code):
        """Get the initial access token.
        """
        req = self.http.get(
            url=constants.ACCESS_TOKEN_URL,
            params=self.get_default_params(code=code),
        )

        if req.status_code < 200 or req.status_code >= 300:
            raise GitHubApiError(req.content, status=req.status_code)

        params = parse.parse_qs(req.content.decode('utf-8'))

        self.access_token = next(iter(params.get('access_token', [])), None)

    def _http_request(self, path, **params):
        """Helper function to hit the GitHub API.
        """
        req = self.http.get(
            url="https://{0}/{1}".format(constants.API_DOMAIN, path.lstrip("/")),
            params=params,
            headers={
                "Authorization": "token {0}".format(self.access_token)
            },
        )
        if req.status_code < 200 or req.status_code >= 300:
            raise GitHubApiError(req.content, status=req.status_code)
        return req.json()

    def get_organizations(self):
        return self._http_request("/user/orgs")

    def get_user(self):
        return self._http_request("/user")

    def get_user_emails(self):
        return self._http_request("/user/emails")

    def is_org_member(self, org_id):
        org_list = self.get_organizations()
        org_id = six.text_type(org_id)
        for o in org_list:
            if six.text_type((o["id"])) == org_id:
                return True
        return False
