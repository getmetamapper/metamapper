# -*- coding: utf-8 -*-
import app.integrations.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class CreateIntegrationConfigTests(cases.GraphQLTestCase):
    """Tests for creating an integration configuration.
    """
    factory = factories.IntegrationConfigFactory

    operation = 'createIntegrationConfig'
    statement = '''
    mutation CreateIntegrationConfig(
      $integration: String!
      $meta: JSONObject!
    ) {
      createIntegrationConfig(input: {
        integration: $integration
        meta: $meta
      }) {
        integrationConfig {
          pk
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'integration': 'PAGERDUTY',
            'meta': {'integration_key': 'woofwoofwoof', 'service': helpers.faker.name()},
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should create a IntegrationConfig scoped to Workspace.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertInstanceCreated(
            model_class=models.IntegrationConfig,
            integration=variables['integration'],
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['OWNER'])
    def test_invalid_integration(self):
        """It should throw a validation error when integration is invalid.
        """
        response = self.execute(variables=self._get_attributes(meta={'integration_key': '', 'service': 'Test Service'}))
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'integrationConfig': None,
            'errors': [
                {
                    'resource': 'IntegrationConfig',
                    'field': 'integration_key',
                    'code': 'blank',
                }
            ],
        })

    @decorators.as_someone(['OWNER'])
    def test_duplicate_integration(self):
        """It should throw a validation error when.
        """
        instance = factories.IntegrationConfigFactory(
            integration='PAGERDUTY',
            meta={'integration_key': 'def', 'service': 'Meow'},
            displayable='Meow',
            workspace=self.workspace)

        variables = self._get_attributes(
            integration=instance.integration,
            meta={'integration_key': 'abc', 'service': 'Meow'})

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'integrationConfig': None,
            'errors': [
                {
                    'resource': 'IntegrationConfig',
                    'field': 'none',
                    'code': 'unique',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class UpdateIntegrationConfigTests(cases.GraphQLTestCase):
    """Tests for updating a integration configuration.
    """
    factory = factories.IntegrationConfigFactory

    operation = 'updateIntegrationConfig'
    statement = '''
    mutation UpdateIntegrationConfig(
      $id: ID!
      $meta: JSONObject
    ) {
      updateIntegrationConfig(input: {
        id: $id
        meta: $meta
      }) {
        integrationConfig {
          integration
          meta
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should update an integration configuration resource.
        """
        resource = self.factory(workspace=self.workspace, auth='meowmeowmeow')
        globalid = helpers.to_global_id('IntegrationConfigType', resource.pk)

        variables = {
            'id': globalid,
            'meta': {'workspace': 'Metamapper', 'token': '<redacted>'},
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        meta = {
            'workspace': variables['meta']['workspace'],
            'bot_name': None,
            'icon_url': None,
        }

        self.assertEqual(response, {
            'integrationConfig': {
                'integration': 'SLACK',
                'meta': meta,
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            meta=meta,
        )

        self.assertNotEqual(resource.auth, '<redacted>')

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('IntegrationConfigType', resource.pk)

        variables = {
            'id': globalid,
            'meta': {'service': 'Metamapper (Kafka)'},
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class DeleteIntegrationConfigTests(cases.GraphQLTestCase):
    """Tests for deleting a integration configuration.
    """
    factory = factories.IntegrationConfigFactory

    operation = 'deleteIntegrationConfig'
    statement = '''
    mutation DeleteIntegrationConfig(
      $id: ID!,
    ) {
      deleteIntegrationConfig(input: {
        id: $id,
      }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should permanently delete the integration configuration.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('IntegrationConfigType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.IntegrationConfig,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('IntegrationConfigType', resource.pk)

        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        globalid = helpers.to_global_id('IntegrationConfigType', '12345')
        response = self.execute(variables={'id': globalid})

        self.assertNotFound(response)
