# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators

import app.integrations.registry as registry


class TestGetAvailableIntegrations(cases.GraphQLTestCase):
    operation = 'availableIntegrations'
    statement = '''
    query GetAvailableIntegrations {
      availableIntegrations {
        id: handler
        name
        installed
        tags
      }
    }
    '''

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(len(results), len(registry.AVAILABLE_INTEGRATIONS))
        self.assertEqual(list(results[0].keys()), [
            'id',
            'name',
            'installed',
            'tags',
        ])

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_unauthorized(self):
        self.assertPermissionDenied(self.execute(self.statement))


class TestGetIntegration(cases.GraphQLTestCase):
    operation = 'integration'
    statement = '''
    query GetIntegration($id: String!) {
      integration(id: $id) {
        id: handler
        name
        tags
        installed
        details {
          name
          label
          type
          isDisplay
          isRequired
          helpText
          options
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query_authorized(self):
        results = self.execute(self.statement, variables={'id': 'SLACK'})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'id': 'SLACK',
            'name': 'Slack',
            'tags': ['Alerting'],
            'installed': False,
            'details': [
                {
                    'name': 'token',
                    'label': 'Token',
                    'type': 'CharField',
                    'isDisplay': False,
                    'isRequired': True,
                    'helpText': 'The authentication token with required scopes.',
                    'options': {'maxLength': 128},
                },
                {
                    'name': 'workspace',
                    'label': 'Workspace',
                    'type': 'CharField',
                    'isDisplay': True,
                    'isRequired': True,
                    'helpText': 'The Slack service this authentication token relates to.',
                    'options': {'maxLength': 50},
                },
                {
                    'name': 'bot_name',
                    'label': 'Bot Name',
                    'type': 'CharField',
                    'isDisplay': False,
                    'isRequired': False,
                    'helpText': 'The name used when publishing messages.',
                    'options': {'maxLength': 20},
                },
                {
                    'name': 'icon_url',
                    'label': 'Icon URL',
                    'type': 'CharField',
                    'isDisplay': False,
                    'isRequired': False,
                    'helpText': 'The url of the icon to appear beside your bot (32px png), leave empty for none.',
                    'options': {'maxLength': None},
                },
            ]
        })

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query_when_not_exists(self):
        results = self.execute(self.statement, variables={'id': 'NOTHING'})
        results = results['data'][self.operation]

        self.assertIsNone(results)

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_unauthorized(self):
        self.assertPermissionDenied(self.execute(self.statement, variables={'id': 'SLACK'}))


class TestGetIntegrationConfigs(cases.GraphQLTestCase):
    factory = factories.IntegrationConfigFactory
    operation = 'integrationConfigs'
    statement = '''
    query GetIntegrationConfigs($id: String!) {
      integrationConfigs(integration: $id) {
        edges {
          node {
            id
            displayable
            meta
            createdAt
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetIntegrationConfigs, self).setUp()

        self.count = 5
        self.integration_configs = self.factory.create_batch(
            self.count,
            integration='SLACK',
            workspace=self.workspace,
        )

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'id': 'SLACK'})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg='Node count should equal number of integation configurations.',
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg='Node count should equal totalCount field.',
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement, variables={'id': 'SLACK'}))

    @decorators.as_someone(['OWNER'])
    def test_query_with_secret(self):
        statement = '''
        query GetIntegrationConfigs($id: String!) {
          integrationConfigs(integration: $id) {
            edges {
              node {
                id
                auth
                meta
                createdAt
              }
            }
          }
        }
        '''
        results = self.execute(statement, variables={'id': 'SLACK'})

        self.assertEqual(results['errors'], [
            {
                'message': 'Cannot query field "auth" on type "IntegrationConfigType". Did you mean "authKeys"?',
                'locations': [{'line': 7, 'column': 17}],
                'status': 400,
            },
        ])
