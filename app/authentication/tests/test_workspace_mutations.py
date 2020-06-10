# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers
import testutils.decorators as decorators

import app.authentication.models as models


class CreateWorkspaceTests(cases.GraphQLTestCase):
    """Test cases for creating a new workspace.
    """
    operation = 'createWorkspace'
    statement = '''
    mutation createWorkspace(
      $name: String!,
      $slug: String!,
    ) {
      createWorkspace(input: {
        name: $name,
        slug: $slug,
      }) {
        workspace {
          name
          slug
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
            'name': 'Aperture Labs',
        }
        attributes.update(**overrides)
        attributes['slug'] = '-'.join(attributes['name'].lower().split())
        return attributes

    def test_create(self):
        """It should create a new Workspace.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'workspace': {
                'name': variables['name'],
                'slug': variables['slug'],
            },
            'errors': None,
        })

        self.assertInstanceCreated(models.Workspace, **variables)

    def test_create_duplicate_slug(self):
        """It should NOT create a new Workspace.
        """
        variables = self._get_attributes()

        factories.WorkspaceFactory(**variables)

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'workspace': None,
            'errors': [
                {
                    'resource': 'Workspace',
                    'field': 'slug',
                    'code': 'exists',
                }
            ],
        })


class UpdateWorkspaceTests(cases.GraphQLTestCase):
    """Test cases for updating an existing workspace.
    """
    factory = factories.WorkspaceFactory

    operation = 'updateWorkspace'
    statement = '''
    mutation updateWorkspace(
      $id: ID!,
      $name: String,
      $slug: String,
    ) {
      updateWorkspace(input: {
        id: $id,
        name: $name,
        slug: $slug,
      }) {
        workspace {
          id
          name
          slug
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def setUp(self):
        super().setUp()

        self.resource = self.workspace
        self.global_id = helpers.to_global_id('WorkspaceType', self.workspace.pk)

    @decorators.as_someone(['OWNER'])
    def test_valid(self):
        """It should update the workspace.
        """
        variables = {
            'id': self.global_id,
            'name': 'Acme Corporation',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'workspace': {
                'id': self.global_id,
                'name': 'Acme Corporation',
                'slug': self.workspace.slug,
            },
            'errors': None,
        })

        self.assertInstanceUpdated(self.resource, name=variables['name'])

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'id': self.global_id,
            'name': 'Acme Corporation',
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)


class DeleteWorkspaceTests(cases.GraphQLTestCase):
    """Test cases for deleting an existing workspace.
    """
    operation = 'deleteWorkspace'
    statement = '''
    mutation deleteWorkspace($id: ID!) {
      deleteWorkspace(input: { id: $id }) {
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
    def test_delete(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.id)
        results = self.execute(variables={'id': node_id})
        results = results['data'][self.operation]

        self.assertOk(results)
        self.assertInstanceDeleted(models.Workspace, id=self.workspace.id)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_delete_when_unauthorized(self):
        node_id = helpers.to_global_id('WorkspaceType', self.workspace.id)
        results = self.execute(variables={'id': node_id})

        self.assertPermissionDenied(results)
        self.assertInstanceExists(models.Workspace, id=self.workspace.id)
