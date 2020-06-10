# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators

from django.test import override_settings
from django.utils import timezone

from app.sso.models import SSOConnection


class TestGetSSOConnections(cases.GraphQLTestCase):
    """Test cases for the fetching sso connections associated
    with the current workspace.
    """
    factory = factories.SSOConnectionFactory
    operation = 'ssoConnections'
    statement = '''
    query {
      ssoConnections {
        edges {
          node {
            id
            entityId
            ssoUrl
            extras
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetSSOConnections, self).setUp()

        self.count = 5
        self.connections = self.factory.create_batch(self.count, workspace=self.workspace)
        self.other_connection = self.factory(workspace=self.other_workspace)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of active domains."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))


class TestGetSSOConnection(cases.GraphQLTestCase):
    """Test cases for the fetching a specific SSO Connection.
    """
    factory = factories.SSOConnectionFactory

    operation = 'ssoConnection'
    statement = '''
    query GetSSOConnection($id: ID!) {
      ssoConnection(id: $id) {
        id
        pk
        name
        provider
        protocol
      }
    }
    '''

    def setUp(self):
        super(TestGetSSOConnection, self).setUp()

        self.connection_kwargs = {
            'provider': SSOConnection.GOOGLE,
            'workspace': self.workspace,
        }

        self.resource = self.factory(**self.connection_kwargs)
        self.global_id = helpers.to_global_id('SSOConnectionType', self.resource.pk)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It should return the requested resource.
        """
        results = self.execute(self.statement, variables={'id': self. global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': self.global_id,
            'pk': self.resource.pk,
            'name': 'google-%s' % self.resource.pk,
            'provider': 'GOOGLE',
            'protocol': 'oauth2',
        })

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        self.assertPermissionDenied(results)


class TestGetSSODomains(cases.GraphQLTestCase):
    """Test cases for the fetching sso domains for a workspace.
    """
    factory = factories.SSODomainFactory

    operation = 'ssoDomains'
    statement = '''
    query GetSSODomains {
      ssoDomains {
        edges {
          node {
            id
            pk
            domain
            verificationStatus
            verificationToken
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetSSODomains, self).setUp()

        self.count = 5
        self.domains = self.factory.create_batch(self.count, workspace=self.workspace)
        self.other_domain = self.factory(workspace=self.other_workspace)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of active domains."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))


class TestGetSSODomain(cases.GraphQLTestCase):
    """Test cases for the fetching a specific SSO Domain.
    """
    factory = factories.SSODomainFactory

    operation = 'ssoDomain'
    statement = '''
    query GetSSODomain($id: ID!) {
      ssoDomain(id: $id) {
        id
        pk
        domain
        verificationStatus
        verificationToken
      }
    }
    '''

    def setUp(self):
        super(TestGetSSODomain, self).setUp()

        self.domain_kwargs = {
            'domain': 'metamapper.io',
            'verified_at': timezone.now(),
            'workspace': self.workspace,
        }

        self.resource = self.factory(**self.domain_kwargs)
        self.resource.save()

        self.global_id = helpers.to_global_id('SSODomainType', self.resource.pk)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It should return the requested resource.
        """
        results = self.execute(self.statement, variables={'id': self. global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': self.global_id,
            'pk': self.resource.pk,
            'domain': 'metamapper.io',
            'verificationStatus': 'SUCCESS',
            'verificationToken': self.resource.verification_token,
        })

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        self.assertPermissionDenied(results)


@override_settings(GOOGLE_ENABLED=True, GITHUB_ENABLED=True)
class TestGetSSOProviders(cases.GraphQLTestCase):
    """Test cases for the fetching the list of supported SSO providers.
    """
    factory = None

    operation = 'ssoProviders'
    statement = '''
    query GetSSOProviders {
      ssoProviders
    }
    '''

    @decorators.as_someone(['MEMBER', 'OWNER', 'OUTSIDER', 'READONLY', 'ANONYMOUS'])
    def test_valid(self):
        """Anyone can access this endpoint.
        """
        response = self.execute(self.statement)
        response = response['data'][self.operation]

        self.assertEqual(response, [
            {
                'provider': 'GITHUB',
                'label': 'Github',
                'protocol': 'oauth2',
            },
            {
                'provider': 'GOOGLE',
                'label': 'Google for Work',
                'protocol': 'oauth2',
            },
            {
                'provider': 'GENERIC',
                'label': 'SAML2',
                'protocol': 'saml2',
            },
        ])


class TestGetSSOPrimaryKey(cases.GraphQLTestCase):
    """Test cases for the fetching the list of supported SSO providers.
    """
    factory = None

    operation = 'ssoPrimaryKey'
    statement = '''
    query GetSSOConnectionPrimaryKey {
      ssoPrimaryKey
    }
    '''

    @decorators.as_someone(['MEMBER', 'OWNER', 'OUTSIDER', 'READONLY'])
    def test_valid(self):
        """Anyone can access this endpoint.
        """
        response1 = self.execute(self.statement)
        response1 = response1['data'][self.operation]

        self.assertEqual(len(response1), 12)

        response2 = self.execute(self.statement)
        response2 = response2['data'][self.operation]

        self.assertEqual(len(response2), 12)
        self.assertNotEqual(response1, response2)

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Unauthenticated users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(self.statement)
        )
