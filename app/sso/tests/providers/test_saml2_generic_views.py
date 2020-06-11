# -*- coding: utf-8 -*-
from base64 import b64decode

from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse

from testutils import factories
from urllib.parse import urlparse, parse_qs


class SAML2AcceptACSViewLoginTests(TestCase):
    """Test cases for `SAML2AcceptACS.login_pipeline` method.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.user = factories.UserFactory()
        self.workspace = factories.WorkspaceFactory()
        self.workspace.grant_membership(self.user, 'READONLY')

    def test_when_connection_does_not_exist(self):
        """It should redirect with an error.
        """
        response = self.client.post(reverse('sso-saml-acs') + '?connection=betDse4R4gus')

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )

    def test_when_connection_is_disabled(self):
        """It should redirect with an error.
        """
        connection = factories.SSOConnectionFactory(workspace=self.workspace, is_enabled=False)

        response = self.client.post(reverse('sso-saml-acs') + f'?connection={connection.pk}')

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )
