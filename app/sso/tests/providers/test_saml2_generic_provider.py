# -*- coding: utf-8 -*-
from unittest import mock

from django.test import TestCase
from django.test.client import RequestFactory

from app.sso.providers.saml2 import provider

from app.sso.exceptions import IdentityNotValid
from app.sso.models import SSOConnection
from app.authentication.models import User, Membership

from testutils.factories import SSOConnectionFactory


class GenericSaml2ProviderTests(TestCase):
    """Test cases for Generic SAML2 provider.
    """

    def setUp(self):
        connection_kwargs = {
            'id': 'SAMLC11x1UsF',
            'provider': SSOConnection.GENERIC,
            'default_permissions': Membership.MEMBER,
            'entity_id': 'saml2-generic-test',
            'sso_url': 'https://app.metamapper.dev/sso/callback',
            'extras': {
                'mappings': {
                    'user_id': 'identity',
                    'user_email': 'email_address',
                    'fname': 'first_name',
                    'lname': 'last_name',
                },
            },
        }

        self.connection = SSOConnectionFactory(**connection_kwargs)
        self.provider = provider.SAML2Provider(self.connection)

    @mock.patch.object(provider.SAML2Provider, 'is_domain_verified', return_value=True)
    def test_authenticate(self, is_domain_verified):
        """It should implement the authenticate method.
        """
        attributes = {
            "identity": ["12345"],
            "email_address": ["picard@enterprise.us"],
            "role": ["Captain"],
            "color": ["Red"],
            "first_name": ["Jean-Luc"],
            "last_name": ["Picard"],
        }

        user = self.provider.authenticate(attributes)

        self.assertTrue(isinstance(user, User))
        self.assertEqual(user.email, "picard@enterprise.us")
        self.assertEqual(user.name, "Jean-Luc Picard")
        self.assertTrue(user.is_staff(self.connection.workspace_id))
        self.assertEqual(set(user.sso_identities.values_list("ident", flat=True)), {"12345"})

    def test_build_identity(self):
        """It should return the expected snapshot.
        """
        attributes = {
            "identity": ["12345"],
            "email_address": ["picard@enterprise.us"],
            "role": ["Captain"],
            "color": ["Red"],
            "first_name": ["Jean-Luc"],
            "last_name": ["Picard"],
        }

        identity = self.provider.build_identity(attributes)

        self.assertEqual(identity, {
            "ident": "12345",
            "email": "picard@enterprise.us",
            "fname": "Jean-Luc",
            "lname": "Picard",
            "email_verified": True,
        })

    def test_build_identity_without_required_attributes(self):
        """It should return an exception.
        """
        attributes = {
            "user_id": ["12345"],
            "email_address": ["picard@enterprise.us"],
            "role": ["Captain"],
            "color": ["Red"],
            "first_name": ["Jean-Luc"],
            "last_name": ["Picard"],
        }

        msg = 'Failed to map SAML attribute: user_id'

        with self.assertRaisesRegexp(IdentityNotValid, msg):
            self.provider.build_identity(attributes)

    def test_get_redirect_url(self):
        """It should build the proper redirect URL without error.
        """
        rf = RequestFactory()
        rq = rf.get('/', HTTP_HOST='app.httphost.dev')
        rs = self.provider.get_redirect_url(rq)

        self.assertEqual(rs[:39], self.connection.sso_url)
        self.assertTrue('app.httphost.dev' in rs)

    def test_attribute_mapping(self):
        """It should retrieve the proper attributes.
        """
        self.assertEqual(self.provider.attribute_mapping(), {
            'user_id': 'identity',
            'user_email': 'email_address',
            'fname': 'first_name',
            'lname': 'last_name',
        })
