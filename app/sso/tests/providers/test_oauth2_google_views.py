# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from unittest import mock

from django.conf import settings
from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse

from testutils import factories
from urllib.parse import urlparse, parse_qs


class GoogleOAuth2ViewSetupTests(TestCase):
    """Test cases for `OAuth2googleView.setup_pipeline` method.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.user = factories.UserFactory()
        self.workspace = factories.WorkspaceFactory()
        self.workspace.grant_membership(self.user, 'READONLY')

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_when_valid(self, google_client):
        """It should redirect with an error.
        """
        domain = 'metamapper.io'

        google_client.return_value.get_user_domain.return_value = domain
        google_client.return_value.refresh_token = 'meowmeowmeow'

        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode((f'login=0&wksp={self.workspace.pk}&uid={self.user.pk}').encode('utf-8')),
        })

        self.user.refresh_from_db()

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            response.url,
            f'{settings.WEBSERVER_ORIGIN}/{self.workspace.pk}/settings/authentication/setup/google?domain={domain}',
        )


class GoogleOAuth2ViewLoginTests(TestCase):
    """Test cases for `OAuth2googleView.login_pipeline` method.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.user = factories.UserFactory()
        self.workspace = factories.WorkspaceFactory()
        self.workspace.grant_membership(self.user, 'READONLY')

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_when_connection_does_not_exist(self, google_client):
        """It should redirect with an error.
        """
        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=betDse4R4gus').encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_when_connection_is_disabled(self, google_client):
        """It should redirect with an error.
        """
        connection = factories.SSOConnectionFactory(workspace=self.workspace, is_enabled=False)

        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_with_not_part_of_google_organization(self, google_client):
        """It should redirect with an error.
        """
        domain = 'metamapper.io'

        google_client.return_value.get_user_domain.return_value = domain
        google_client.return_value.get_user.return_value = {
            "sub": "1234",
            "email": self.user.email,
            "given_name": self.user.fname,
            "family_name": self.user.lname,
            "email_verified": True,
        }

        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            is_enabled=True,
            extras={'domain': 'metamapper.dev'},
        )

        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            f'The domain for your Google account ({domain}) is not allowed to authenticate with this provider.',
        )

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_when_valid(self, google_client):
        """It authenticate the user.
        """
        domain = self.user.email.split("@")[-1]

        google_client.return_value.get_user_domain.return_value = domain
        google_client.return_value.get_user.return_value = {
            "sub": "1234",
            "email": self.user.email,
            "given_name": self.user.fname,
            "family_name": self.user.lname,
            "email_verified": True,
        }

        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            is_enabled=True,
            extras={'domain': domain},
        )

        sso_domain = factories.SSODomainFactory(
            workspace=self.workspace,
            domain=domain,
        )
        sso_domain.mark_as_verified()

        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        self.user.refresh_from_db()

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            response.url,
            f'{settings.WEBSERVER_ORIGIN}/{self.workspace.slug}/sso/{self.user.pk}/{self.user.sso_access_token}',
        )

    @mock.patch('app.sso.providers.oauth2.google.views.GoogleClient')
    def test_when_domain_is_not_verified(self, google_client):
        """It should redirect with an error.
        """
        domain = self.user.email.split("@")[-1]

        google_client.return_value.get_user_domain.return_value = domain
        google_client.return_value.get_user.return_value = {
            "sub": "1234",
            "email": self.user.email,
            "given_name": self.user.fname,
            "family_name": self.user.lname,
            "email_verified": True,
        }

        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            is_enabled=True,
            extras={'domain': domain},
        )

        response = self.client.get(reverse('sso-oauth2-google'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'Domain is not authorized for the provided workspace.',
        )
