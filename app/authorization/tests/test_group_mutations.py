# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers

import app.authorization.models as models


class CreateGroupTests(cases.GraphQLTestCase):
    """Tests for creating a Group via the mutation.
    """
    operation = 'createGroup'
    statement = '''
    mutation createGroup(
      $name: String!,
      $description: String,
    ) {
      createGroup(input: {
        name: $name,
        description: $description,
      }) {
        group {
          name
          description
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
            'name': 'Data Engineering',
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['OWNER'])
    def test_create(self):
        """It should create a new Group.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'group': {
                'name': variables['name'],
                'description': variables.get('description'),
            },
            'errors': None,
        })

        self.assertInstanceCreated(models.Group, **variables)

    @decorators.as_someone(['OWNER'])
    def test_create_with_duplicate_name_outside_workspace(self):
        """It should create a new Group since the unique constraint is restricted to the workspace.
        """
        variables = self._get_attributes()

        factories.GroupFactory(workspace_id=self.other_workspace.pk, **variables)

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'group': {
                'name': variables['name'],
                'description': variables.get('description'),
            },
            'errors': None,
        })

        self.assertInstanceCreated(models.Group, **variables)

    @decorators.as_someone(['OWNER'])
    def test_create_with_duplicate_name_within_workspace(self):
        """It should NOT create a new Group.
        """
        variables = self._get_attributes()
        factories.GroupFactory(workspace_id=self.workspace.pk, **variables)

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'group': None,
            'errors': [
                {
                    'resource': 'Group',
                    'field': 'none',
                    'code': 'unique',
                }
            ],
        })

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        variables = self._get_attributes()
        self.assertPermissionDenied(self.execute(variables=variables))


class UpdateGroupTests(cases.GraphQLTestCase):
    """Tests for updating a Group via the mutation.
    """
    factory = factories.GroupFactory

    operation = 'updateGroup'
    statement = '''
    mutation updateGroup(
      $id: ID!,
      $name: String,
      $description: String,
    ) {
      updateGroup(input: {
        id: $id,
        name: $name,
        description: $description,
      }) {
        group {
          id
          name
          description
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
        """It should update the Group.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'HQ Office',
            'description': 'Team members that sit in the headquarter office.',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'group': variables,
            'errors': None
        })

        self.assertInstanceUpdated(
            instance=resource,
            name=variables['name'],
            description=variables['description'],
        )

    @decorators.as_someone(['OWNER'])
    def test_invalid_validators(self):
        """It should throw a validation error when a validators are invalid.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        variables = {
            'id': globalid,
            'name': '',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'group': None,
            'errors': [
                {
                    'resource': 'Group',
                    'field': 'name',
                    'code': 'blank',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        variables = {
            'id': globalid,
            'name': 'New Name',
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class DeleteGroupTests(cases.GraphQLTestCase):
    """Tests for deleting a Group via the mutation.
    """
    factory = factories.GroupFactory

    operation = 'deleteGroup'
    statement = '''
    mutation DeleteGroup(
      $id: ID!,
    ) {
      deleteGroup(input: {
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
        """It should permanently delete the Group.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Group,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        globalid = helpers.to_global_id('GroupType', '12345')
        response = self.execute(variables={'id': globalid})

        self.assertNotFound(response)


class AddUserToGroupTests(cases.GraphQLTestCase):
    """Tests for adding the User to a Group via the mutation.
    """
    factory = factories.GroupFactory

    operation = 'addUserToGroup'
    statement = '''
    mutation AddUserToGroup(
      $id: ID!,
      $userId: ID!,
    ) {
      addUserToGroup(input: {
        id: $id,
        userId: $userId,
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
        """It should add the user to the group.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        user = self.users['READONLY']
        user_globalid = helpers.to_global_id('UserType', user.pk)

        response = self.execute(variables={'id': globalid, 'userId': user_globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertTrue(user.groups.filter(name=resource.name).exists())

    @decorators.as_someone(['OWNER'])
    def test_fails_to_add_outsider(self):
        """It should add the user to the group.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        user = self.users['OUTSIDER']
        user_globalid = helpers.to_global_id('UserType', user.pk)

        response = self.execute(variables={'id': globalid, 'userId': user_globalid})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'User',
                    'field': 'user',
                    'code': 'no_membership',
                },
            ]
        })
        self.assertFalse(user.groups.filter(name=resource.name).exists())

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        user = self.users['READONLY']
        user_globalid = helpers.to_global_id('UserType', user.pk)

        response = self.execute(variables={'id': globalid, 'userId': user_globalid})

        self.assertPermissionDenied(response)
        self.assertFalse(user.groups.filter(name=resource.name).exists())


class RemoveUserFromGroupTests(cases.GraphQLTestCase):
    """Tests for removing the User from a Group via the mutation.
    """
    factory = factories.GroupFactory

    operation = 'removeUserFromGroup'
    statement = '''
    mutation RemoveUserFromGroup(
      $id: ID!,
      $userId: ID!,
    ) {
      removeUserFromGroup(input: {
        id: $id,
        userId: $userId,
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
        """It should remove the user from the group.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        user = self.users['READONLY']
        user_globalid = helpers.to_global_id('UserType', user.pk)

        resource.user_set.add(user)

        response = self.execute(variables={'id': globalid, 'userId': user_globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertFalse(user.groups.filter(name=resource.name).exists())

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('GroupType', resource.pk)

        user = self.users['READONLY']
        user_globalid = helpers.to_global_id('UserType', user.pk)

        resource.user_set.add(user)

        response = self.execute(variables={'id': globalid, 'userId': user_globalid})

        self.assertPermissionDenied(response)
        self.assertTrue(user.groups.filter(name=resource.name).exists())
