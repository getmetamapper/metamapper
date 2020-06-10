# -*- coding: utf-8 -*-
import unittest.mock as mock

from django.test import TestCase
from django.test.client import RequestFactory

from app.sso.providers.oauth2.google import client
from app.sso.providers.oauth2.google import provider

from app.sso.models import SSOConnection
from app.authentication.models import User, Membership

from testutils.factories import SSOConnectionFactory


class GoogleOAuth2ProviderTests(TestCase):
    """Test cases for Google SSO provider.
    """

    def setUp(self):
        connection_kwargs = {
            'id': 'GOONC11x1UsF',
            'provider': SSOConnection.GOOGLE,
            'default_permissions': Membership.MEMBER,
        }

        self.client = client.GoogleClient()
        self.connection = SSOConnectionFactory(**connection_kwargs)
        self.provider = provider.GoogleOAuth2Provider(self.connection, self.client)

    def test_authenticate(self):
        """It should implement the authenticate method.
        """
        attributes = {
            "id": "54321",
            "sub": "12345",
            "email": "picard@enterprise.us",
            "email_verified": True,
            "given_name": "Jean-Luc",
            "family_name": "Picard",
            "extras": {
                "role": "Captain",
            },
            "color": "Red",
        }

        user = self.provider.authenticate(attributes)

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, "picard@enterprise.us")
        self.assertTrue(user.is_staff(self.connection.workspace_id))
        self.assertEqual(set(user.sso_identities.values_list("ident", flat=True)), {"12345"})

    def test_build_identity(self):
        """It should return the expected snapshot.
        """
        attributes = {
            "id": "54321",
            "sub": "12345",
            "email": "picard@enterprise.us",
            "email_verified": True,
            "given_name": "Jean-Luc",
            "family_name": "Picard",
            "extras": {
                "role": "Captain",
            },
            "color": "Red",
        }

        identity = self.provider.build_identity(attributes)

        self.assertEqual(identity, {
            "ident": "12345",
            "email": "picard@enterprise.us",
            "fname": "Jean-Luc",
            "lname": "Picard",
            "email_verified": True,
        })

    @mock.patch.object(provider.GoogleOAuth2Provider, 'get_redirect_uri')
    @mock.patch.object(provider.GoogleOAuth2Provider, 'get_client_id')
    def test_get_redirect_url(self, get_client_id, get_redirect_uri):
        """It should build the proper redirect URL without error.
        """
        get_client_id.return_value = 'prosciutto'
        get_redirect_uri.return_value = 'https://www.metamapper.io/oauth2/google/callback'

        rf = RequestFactory()
        rq = rf.get('/')

        self.assertEqual(
            self.provider.get_redirect_url(rq),
            ('https://accounts.google.com/o/oauth2/auth'
             '?client_id=prosciutto'
             '&scope=openid+email+profile'
             '&state=Y29ubmVjdGlvbj1HT09OQzExeDFVc0Y%3D'
             '&access_type=offline'
             '&response_type=code'
             '&redirect_uri=https%3A%2F%2Fwww.metamapper.io%2Foauth2%2Fgoogle%2Fcallback'),
        )
