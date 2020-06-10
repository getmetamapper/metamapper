# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from unittest import mock

from django.conf import settings
from django.http import HttpResponseRedirect
from django.test import TestCase, Client
from django.urls import reverse

from testutils import factories
from urllib.parse import urlparse, parse_qs


class GithubOAuth2ViewSetupTests(TestCase):
    """Test cases for `OAuth2GithubView.setup_pipeline` method.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.user = factories.UserFactory()
        self.workspace = factories.WorkspaceFactory()
        self.workspace.grant_membership(self.user, 'READONLY')

    @mock.patch('app.sso.providers.oauth2.github.views.GithubClient')
    def test_when_valid(self, github_client):
        """It should redirect with an error.
        """
        github_client.return_value.is_org_member.return_value = True
        github_client.return_value.get_user.return_value = {
            "uid": self.user.pk,
            "id": "1234",
            "email": self.user.email,
            "verified": True,
        }
        github_client.return_value.access_token = 'meowmeowmeow'

        response = self.client.get(reverse('sso-oauth2-github'), {
            'code': 'meowmeowmeow',
            'state': b64encode((f'login=0&wksp={self.workspace.pk}&uid={self.user.pk}').encode('utf-8')),
        })

        self.user.refresh_from_db()

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            response.url,
            f'{settings.WEBSERVER_ORIGIN}/{self.workspace.pk}/settings/authentication/setup/github',
        )


class GithubOAuth2ViewLoginTests(TestCase):
    """Test cases for `OAuth2GithubView.login_pipeline` method.
    """
    def setUp(self):
        self.client = Client(HTTP_HOST='example.com')
        self.user = factories.UserFactory()
        self.workspace = factories.WorkspaceFactory()
        self.workspace.grant_membership(self.user, 'READONLY')

    @mock.patch('app.sso.providers.oauth2.github.views.GithubClient')
    def test_when_connection_does_not_exist(self, github_client):
        """It should redirect with an error.
        """
        response = self.client.get(reverse('sso-oauth2-github'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=betDse4R4gus').encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )

    @mock.patch('app.sso.providers.oauth2.github.views.GithubClient')
    def test_when_connection_is_disabled(self, github_client):
        """It should redirect with an error.
        """
        connection = factories.SSOConnectionFactory(workspace=self.workspace, is_enabled=False)

        response = self.client.get(reverse('sso-oauth2-github'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'The workspace does not exist or does not have SSO enabled.',
        )

    @mock.patch('app.sso.providers.oauth2.github.views.GithubClient')
    def test_with_not_part_of_github_organization(self, github_client):
        """It should redirect with an error.
        """
        github_client.return_value.is_org_member.return_value = False
        github_client.return_value.get_user.return_value = {
            "uid": self.user.pk,
            "id": "1234",
        }

        connection = factories.SSOConnectionFactory(workspace=self.workspace, is_enabled=True)

        response = self.client.get(reverse('sso-oauth2-github'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        urlparams = parse_qs(urlparse(response.url).query)

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            b64decode(urlparams['error'][0]).decode('utf-8'),
            'You are not an authorized member of the connected GitHub organization.',
        )

    @mock.patch('app.sso.providers.oauth2.github.views.GithubClient')
    def test_when_valid(self, github_client):
        """It should redirect with an error.
        """
        github_client.return_value.is_org_member.return_value = True
        github_client.return_value.get_user.return_value = {
            "uid": self.user.pk,
            "id": "1234",
            "email": self.user.email,
            "verified": True,
        }

        connection = factories.SSOConnectionFactory(workspace=self.workspace, is_enabled=True)

        response = self.client.get(reverse('sso-oauth2-github'), {
            'code': 'meowmeowmeow',
            'state': b64encode(('connection=%s' % connection.pk).encode('utf-8')),
        })

        self.user.refresh_from_db()

        self.assertTrue(isinstance(response, (HttpResponseRedirect,)))
        self.assertEqual(
            response.url,
            f'{settings.WEBSERVER_ORIGIN}/{self.workspace.slug}/sso/{self.user.pk}/{self.user.sso_access_token}',
        )
