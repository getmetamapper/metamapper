# -*- coding: utf-8 -*-
from app.integrations.client import ApiClient
from app.integrations.errors import ApiError


class SlackClient(ApiClient):
    """Client for sending API calls to Slack.
    """
    allow_redirects = False

    base_url = "https://slack.com/api"

    def __init__(self, bot_token):
        self.bot_token = bot_token
        super().__init__()

    def request(self, method, path, headers=None, data=None, params=None):
        """Send an authenticated API request.
        """
        if not headers:
            headers = {"Content-Type": "application/json"}

        if not data:
            data = {}

        headers.update({"Authorization": "Bearer %s" % self.bot_token})

        response = self._request(method, path, headers=headers, json=data, params=params)

        if not response["ok"]:
            raise ApiError("API call failed: %s" % response.get("error", "unknown"))

        return response
