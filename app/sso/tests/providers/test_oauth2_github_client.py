# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from django.conf import settings

from app.sso.providers.oauth2.github import client
from app.sso.providers.oauth2.github import constants


class GithubClientTests(unittest.TestCase):
    """Test cases for accessing Github API.
    """

    def setUp(self):
        self.client = client.GithubClient()

    def test_get_default_params(self):
        """Confirm the structure of the `default_params`.
        """
        self.assertEqual(
            set(self.client.get_default_params(code='12345').keys()),
            {'client_id', 'client_secret', 'code'},
        )

    @mock.patch('requests.Session.get')
    def test_set_access_token_when_valid_response(self, http_get):
        """It should consume a valid HTTP response.
        """
        mock_response = mock.MagicMock(
            status_code=200,
            content=b'access_token=e72e16c7e42f292c6912e7710c838347ae178b4a&token_type=bearer',
        )

        http_get.return_value = mock_response

        self.client.set_access_token('whatever')

        self.assertEqual(self.client.access_token, 'e72e16c7e42f292c6912e7710c838347ae178b4a')

        http_get.assert_called()
        http_get.assert_called_with(
            url=constants.ACCESS_TOKEN_URL,
            params={
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'code': 'whatever',
            }
        )

    @mock.patch('requests.Session.get')
    def test_set_access_token_when_invalid_response(self, http_get):
        """It should reject an invalid HTTP response.
        """
        mock_response = mock.MagicMock(status_code=400)
        http_get.return_value = mock_response

        with self.assertRaises(client.GitHubApiError):
            self.client.set_access_token('surething')

        http_get.assert_called()
        http_get.assert_called_with(
            url=constants.ACCESS_TOKEN_URL,
            params={
                'client_id': settings.GITHUB_CLIENT_ID,
                'client_secret': settings.GITHUB_CLIENT_SECRET,
                'code': 'surething',
            }
        )

    @mock.patch.object(client.GithubClient, 'get_organizations')
    def test_is_org_member_truthy(self, get_organizations):
        """Check if user is part of Github organization.
        """
        get_organizations.return_value = [
            {"id": "12345"},
            {"id": "56789"},
            {"id": "10231"},
        ]

        assert self.client.is_org_member("56789")

    @mock.patch.object(client.GithubClient, 'get_organizations')
    def test_is_org_member_falsey(self, get_organizations):
        """Check if user is part of Github organization.
        """
        get_organizations.return_value = [
            {"id": "12345"},
            {"id": "56789"},
            {"id": "10231"},
        ]

        assert not self.client.is_org_member("55555")
