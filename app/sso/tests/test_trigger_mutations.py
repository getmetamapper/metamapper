# -*- coding: utf-8 -*-
import unittest.mock as mock

import django.conf as conf
import app.sso.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories


class UserExistsCheckTests(cases.GraphQLTestCase):
    """Tests for checking if a user exists and has SSO enabled.
    """
    operation = 'userExistsCheck'
    statement = '''
    mutation CheckUserExists($email: String!) {
      userExistsCheck(email: $email) {
        ok
        email
        isSSOForced
        workspaceSlug
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.sso_domain = models.SSODomain.objects.create(
            workspace=self.workspace,
            domain='metamapper.io',
        )

        self.sso_connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            is_enabled=True,
        )

        self.email = 'owner@metamapper.io'

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_when_email_exists(self):
        """It should return that the email exists.
        """
        response = self.execute(variables={'email': self.email})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': True,
            'email': self.email,
            'isSSOForced': False,
            'workspaceSlug': None,
        })

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_when_email_does_not_exists(self):
        """It should return that the email does not exist.
        """
        email = 'takeshi.kovacs@ctac.org'

        response = self.execute(variables={'email': email})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'email': email,
            'isSSOForced': False,
            'workspaceSlug': None,
        })

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_when_domain_is_verified(self):
        """It should return True for SSO redirects.
        """
        self.workspace.active_sso = self.sso_connection
        self.workspace.save()
        self.sso_domain.mark_as_verified()

        response = self.execute(variables={'email': self.email})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': True,
            'email': self.email,
            'isSSOForced': True,
            'workspaceSlug': self.workspace.slug,
        })

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_when_domain_is_not_verified(self):
        """It should return False for SSO redirects.
        """
        self.workspace.active_sso = self.sso_connection
        self.workspace.save()

        response = self.execute(variables={'email': self.email})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': True,
            'email': self.email,
            'isSSOForced': False,
            'workspaceSlug': None,
        })

    @decorators.as_someone(['MEMBER', 'ANONYMOUS'])
    def test_when_domain_is_verified_but_no_active_sso(self):
        """It should return False for SSO redirects.
        """
        response = self.execute(variables={'email': self.email})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': True,
            'email': self.email,
            'isSSOForced': False,
            'workspaceSlug': None,
        })


class TriggerSingleSignOnTests(cases.GraphQLTestCase):
    """Tests for executing a SSO action.
    """
    operation = 'triggerSingleSignOn'
    statement = '''
    mutation TriggerSingleSignOn($workspaceSlug: String!) {
      triggerSingleSignOn(
        workspaceSlug: $workspaceSlug
      ) {
        redirectUrl
      }
    }
    '''

    @decorators.as_someone(['ANONYMOUS'])
    @mock.patch('app.sso.providers.saml2.provider.prepare_auth_request')
    def test_when_saml2_generic(self, mock_auth_request):
        the_mock = mock.MagicMock()
        the_mock.login.return_value = 'http://this-is-the-sso-url/hi'
        mock_auth_request.return_value = the_mock

        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            provider=models.SSOConnection.GENERIC,
            is_enabled=True,
            entity_id='urn:auth0:metamapper',
            x509cert=None,
            extras={
                'mappings': {
                    'user_id': 'identifier',
                    'user_email': 'user_email',
                    'fname': 'first_name',
                    'lname': 'last_name',
                },
            },
        )

        self.workspace.active_sso = connection
        self.workspace.save()

        variables = {
            'workspaceSlug': self.workspace.slug
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'redirectUrl': 'http://this-is-the-sso-url/hi',
        })

    @decorators.as_someone(['ANONYMOUS'])
    def test_when_oauth2_google(self):
        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            provider=models.SSOConnection.GOOGLE,
            is_enabled=True,
            entity_id='metamapper.io',
            sso_url=None,
            x509cert=None,
            extras={
                'domain': 'metamapper.io',
            },
        )

        self.workspace.active_sso = connection
        self.workspace.save()

        variables = {
            'workspaceSlug': self.workspace.slug
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]
        redirect = (
            'https://accounts.google.com/o/oauth2/auth'
            '?client_id={}'
            '&scope=openid+email+profile'
        ).format(conf.settings.GOOGLE_CLIENT_ID)

        self.assertTrue(redirect in response['redirectUrl'])

    @decorators.as_someone(['ANONYMOUS'])
    def test_when_oauth2_github(self):
        connection = factories.SSOConnectionFactory(
            workspace=self.workspace,
            provider=models.SSOConnection.GITHUB,
            is_enabled=True,
            entity_id='metamapper-io',
            sso_url=None,
            x509cert=None,
            extras={
                'login': 'metamapper-io',
                'ident': '543210',
            },
        )

        self.workspace.active_sso = connection
        self.workspace.save()

        variables = {
            'workspaceSlug': self.workspace.slug
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        redirect = (
            'https://github.com/login/oauth/authorize'
            '?client_id={}'
            '&scope=user%3Aemail%2Cread%3Aorg%2Crepo'
        ).format(conf.settings.GITHUB_CLIENT_ID)

        self.assertTrue(redirect in response['redirectUrl'])

    @decorators.as_someone(['ANONYMOUS'])
    def test_when_disabled(self):
        variables = {
            'workspaceSlug': self.workspace.slug
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'redirectUrl': None,
        })
