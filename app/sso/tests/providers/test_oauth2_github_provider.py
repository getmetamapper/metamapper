# -*- coding: utf-8 -*-
from unittest import mock

from django.test import TestCase
from django.test.client import RequestFactory

from app.sso.providers.oauth2.github import client
from app.sso.providers.oauth2.github import provider

from app.sso.models import SSOConnection
from app.authentication.models import User, Membership

from testutils.factories import SSOConnectionFactory


class GithubOAuth2ProviderTests(TestCase):
    """Test cases for Github SSO provider.
    """

    def setUp(self):
        connection_kwargs = {
            'id': 'GITNC11x1UsF',
            'provider': SSOConnection.GITHUB,
            'default_permissions': Membership.MEMBER,
        }

        self.client = client.GithubClient()
        self.connection = SSOConnectionFactory(**connection_kwargs)
        self.provider = provider.GithubOAuth2Provider(self.connection, self.client)

    @mock.patch.object(provider.GithubOAuth2Provider, 'is_domain_verified', return_value=True)
    def test_authenticate(self, is_domain_verified):
        """It should implement the authenticate method.
        """
        attributes = {
            "id": "12345",
            "sub": "1212321345",
            "email": "picard@enterprise.us",
            "given_name": "Jean-Luc",
            "family_name": "Picard",
            "extras": {
                "role": "Captain",
            },
            "color": "Red",
            "verified": True,
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
            "id": "12345",
            "email": "picard@enterprise.us",
            "verified": False,
            "extras": {
                "role": "Captain",
            },
            "color": "Red",
        }

        identity = self.provider.build_identity(attributes)

        self.assertEqual(identity, {
            "ident": "12345",
            "email": "picard@enterprise.us",
            "fname": "",
            "lname": "",
            "email_verified": False,
        })

    @mock.patch.object(provider.GithubOAuth2Provider, 'get_redirect_uri')
    @mock.patch.object(provider.GithubOAuth2Provider, 'get_client_id')
    def test_get_redirect_url(self, get_client_id, get_redirect_uri):
        """It should build the proper redirect URL without error.
        """
        get_client_id.return_value = 'prosciutto'
        get_redirect_uri.return_value = 'https://www.metamapper.io/oauth2/github/callback'

        rf = RequestFactory()
        rq = rf.get('/')

        self.assertEqual(
            self.provider.get_redirect_url(rq),
            ('https://github.com/login/oauth/authorize'
             '?client_id=prosciutto'
             '&scope=user%3Aemail%2Cread%3Aorg%2Crepo'
             '&redirect_uri=https%3A%2F%2Fwww.metamapper.io%2Foauth2%2Fgithub%2Fcallback'
             '%3Fstate%3DY29ubmVjdGlvbj1HSVROQzExeDFVc0Y%3D'),
        )
