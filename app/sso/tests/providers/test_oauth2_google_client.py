# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock
import datetime as dt

from django.conf import settings
from django.utils import timezone

from app.sso.providers.oauth2.google import client
from app.sso.providers.oauth2.google import constants


class GoogleClientTests(unittest.TestCase):
    """Test cases for accessing Google API.
    """

    def setUp(self):
        self.client = client.GoogleClient()

    def test_get_default_params(self):
        """Confirm the structure of the `default_params`.
        """
        self.assertEqual(
            set(self.client.get_default_params(code='12345').keys()),
            {'client_id', 'client_secret', 'code'},
        )

    @mock.patch.object(client.GoogleClient, 'get_access_token')
    def test_get_or_refresh_access_token(self, get_access_token):
        """It should set the `access_token` property.
        """
        get_access_token.return_value = 'thisisthetoken'

        token = self.client.get_or_refresh_access_token()

        self.assertEqual(self.client.access_token, token)
        self.assertEqual(token, 'thisisthetoken')

    @mock.patch.object(client.GoogleClient, 'get_access_token')
    def test_get_or_refresh_access_token_when_expired(self, get_access_token):
        """It should set the `access_token` property when the token is expired.
        """
        self.client.access_token = 'something'
        self.client.issued_at = timezone.now() - dt.timedelta(hours=2)

        get_access_token.return_value = 'somethingelse'

        token = self.client.get_or_refresh_access_token()

        self.assertEqual(self.client.access_token, token)
        self.assertEqual(token, 'somethingelse')
        self.assertTrue(timezone.now() - dt.timedelta(minutes=1) < self.client.issued_at)

    @mock.patch('requests.Session.post')
    def test_get_access_token_on_success(self, http_post):
        """It should process an valid HTTP response.
        """
        mock_response = mock.MagicMock(status_code=200)
        mock_response.json.return_value = {
            'access_token': 'meowmeowmeow',
        }

        http_post.return_value = mock_response

        self.assertEqual(self.client.get_access_token(), 'meowmeowmeow')

    @mock.patch('requests.Session.post')
    def test_get_access_token_on_failure(self, http_post):
        """It should reject an invalid HTTP response.
        """
        mock_response = mock.MagicMock(status_code=400)
        http_post.return_value = mock_response

        with self.assertRaises(client.GoogleApiError):
            self.client.get_access_token()

        http_post.assert_called()
        http_post.assert_called_with(
            url=constants.REFRESH_TOKEN_URL,
            params={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'refresh_token': self.client.refresh_token,
                'grant_type': 'refresh_token',
            }
        )

    @mock.patch('requests.Session.post')
    def test_set_access_token_on_success(self, http_post):
        """It should process an valid HTTP response.
        """
        mock_response = mock.MagicMock(status_code=200)
        mock_response.json.return_value = {
            'access_token': 'meowmeowmeow',
            'refresh_token': 'woofwoofwoof',
        }

        http_post.return_value = mock_response

        self.client.set_access_token('12345')

        self.assertEqual(self.client.access_token, 'meowmeowmeow')
        self.assertEqual(self.client.refresh_token, 'woofwoofwoof')
        self.assertFalse(self.client.issued_at is None)

    @mock.patch('requests.Session.post')
    def test_set_access_token_on_failure(self, http_post):
        """It should reject an invalid HTTP response.
        """
        mock_response = mock.MagicMock(status_code=400)
        http_post.return_value = mock_response

        with self.assertRaises(client.GoogleApiError):
            self.client.set_access_token('surething')

        http_post.assert_called()
        http_post.assert_called_with(
            url=constants.ACCESS_TOKEN_URL,
            params={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': 'surething',
                'grant_type': 'authorization_code',
                'redirect_uri': f'{settings.WEBSERVER_ORIGIN}/oauth2/google/callback',
            }
        )

    @mock.patch.object(client.GoogleClient, 'get_user')
    def test_get_user_domain(self, get_user):
        """Properly parse the results from `get_user`.
        """
        get_user.return_value = {
            "scope": "https://www.googleapis.com/auth/userinfo.profile",
            "exp": "1554094721",
            "expires_in": "3326",
            "access_type": "offline",
            "email": "scott@metamapper.io",
        }

        self.assertEqual(self.client.get_user_domain(), "metamapper.io")
