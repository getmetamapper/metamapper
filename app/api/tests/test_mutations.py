# -*- coding: utf-8 -*-
import app.api.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class CreateApiTokenTests(cases.GraphQLTestCase):
    """Tests for creating a API token.
    """
    factory = factories.ApiTokenFactory

    operation = 'createApiToken'
    statement = '''
    mutation CreateApiToken(
      $name: String!,
      $isEnabled: Boolean,
    ) {
      createApiToken(input: {
        name: $name,
        isEnabled: $isEnabled,
      }) {
        apiToken {
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
            'name': helpers.faker.name(),
            'isEnabled': True,
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should create a ApiToken scoped to Workspace.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertInstanceCreated(
            model_class=models.ApiToken,
            name=variables['name'],
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['OWNER'])
    def test_invalid_name(self):
        """It should throw a validation error when name is invalid.
        """
        response = self.execute(variables=self._get_attributes(name=''))
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'apiToken': None,
            'errors': [
                {
                    'resource': 'ApiToken',
                    'field': 'name',
                    'code': 'blank',
                }
            ],
        })

    @decorators.as_someone(['OWNER'])
    def test_duplicate_name(self):
        """It should throw a validation error when.
        """
        instance = factories.ApiTokenFactory(name="Test Token", workspace=self.workspace)
        variables = self._get_attributes(name=instance.name)

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'apiToken': None,
            'errors': [
                {
                    'resource': 'ApiToken',
                    'field': 'name',
                    'code': 'exists',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(variables=self._get_attributes()))


class UpdateApiTokenTests(cases.GraphQLTestCase):
    """Tests for updating a API token.
    """
    factory = factories.ApiTokenFactory

    operation = 'updateApiToken'
    statement = '''
    mutation UpdateApiToken(
      $id: ID!,
      $isEnabled: Boolean
    ) {
      updateApiToken(input: {
        id: $id,
        isEnabled: $isEnabled,
      }) {
        apiToken {
          name
          isEnabled
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
        """It should update an API token resource.
        """
        resource = self.factory(workspace=self.workspace, is_enabled=True)
        globalid = helpers.to_global_id('ApiTokenType', resource.pk)

        variables = {
            'id': globalid,
            'isEnabled': False,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'apiToken': {
                'name': resource.name,
                'isEnabled': False,
            },
            'errors': None
        })

        self.assertInstanceUpdated(
            instance=resource,
            isEnabled=variables['isEnabled'],
        )

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('ApiTokenType', resource.pk)

        variables = {
            'id': globalid,
            'is_enabled': False,
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class DeleteApiTokenTests(cases.GraphQLTestCase):
    """Tests for deleting a API token.
    """
    factory = factories.ApiTokenFactory

    operation = 'deleteApiToken'
    statement = '''
    mutation DeleteApiToken(
      $id: ID!,
    ) {
      deleteApiToken(input: {
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
        """It should permanently delete the API token.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('ApiTokenType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.ApiToken,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('ApiTokenType', resource.pk)

        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        globalid = helpers.to_global_id('ApiTokenType', '12345')
        response = self.execute(variables={'id': globalid})

        self.assertNotFound(response)
