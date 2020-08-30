# -*- coding: utf-8 -*-
import random
import unittest.mock as mock

import app.audit.models as audit

import app.definitions.models as models
import app.definitions.serializers as serializers

import app.inspector.service as inspector

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class CreateDatastoreTests(cases.GraphQLTestCase):
    """Tests for creating a datastore.
    """
    operation = 'createDatastore'
    statement = '''
    mutation CreateDatastore(
      $name: String!,
      $tags: [String],
      $engine: String!,
      $username: String!,
      $password: String!,
      $database: String!,
      $host: String!,
      $port: Int!,
      $sshEnabled: Boolean,
      $sshHost: String,
      $sshUser: String,
      $sshPort: Int,
    ) {
      createDatastore(input: {
        name: $name,
        tags: $tags,
        engine: $engine,
        username: $username,
        password: $password,
        database: $database,
        host: $host,
        port: $port,
        sshEnabled: $sshEnabled,
        sshHost: $sshHost,
        sshUser: $sshUser,
        sshPort: $sshPort,
      }) {
        datastore {
          name
          isEnabled
          jdbcConnection {
            engine
          }
          sshConfig {
            isEnabled
            host
            port
          }
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
            'engine': random.choice(['oracle', 'postgresql', 'sqlserver']),
            'username': 'admin',
            'password': 'password1234',
            'database': 'product_db',
            'host': 'web-86.cortez.net',
            'port': 5439,
        }
        attributes.update(**overrides)
        return attributes

    @mock.patch('app.definitions.serializers.JdbcConnectionSerializer.validate_connection')
    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_without_ssh_details(self, start_run, validate_connection):
        """It should not require SSH information for creation.
        """
        variables = self._get_attributes()

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'name': variables['name'],
                'isEnabled': True,
                'jdbcConnection': {
                    'engine': variables['engine'],
                },
                'sshConfig': {
                    'isEnabled': False,
                    'host': None,
                    'port': None,
                }
            },
            'errors': None
        })

        self.assertInstanceCreated(models.Datastore, name=variables['name'])

        datastore = models.Datastore.objects.get(name=variables['name'])
        self.assertTrue(self.user.has_perm('view_datastore', datastore))

    @mock.patch('app.definitions.serializers.JdbcConnectionSerializer.validate_connection')
    @mock.patch('app.revisioner.tasks.core.start_revisioner_run.apply_async')
    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_with_ssh_details(self, start_run, validate_connection):
        """It should attach SSH information on creation.
        """
        variables = self._get_attributes(
            sshEnabled=True,
            sshHost='127.0.0.1',
            sshPort=22,
            sshUser='scott',
        )

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'name': variables['name'],
                'isEnabled': True,
                'jdbcConnection': {
                    'engine': variables['engine'],
                },
                'sshConfig': {
                    'isEnabled': True,
                    'host': variables['sshHost'],
                    'port': variables['sshPort'],
                }
            },
            'errors': None
        })

        self.assertInstanceCreated(models.Datastore, name=variables['name'])

        datastore = models.Datastore.objects.get(name=variables['name'])
        self.assertTrue(self.user.has_perm('view_datastore', datastore))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        variables = self._get_attributes()
        response = self.execute(variables=variables)
        self.assertPermissionDenied(response)


class UpdateDatastoreMetadataTests(cases.GraphQLTestCase):
    """Tests for updating a datastore.
    """
    factory = factories.DatastoreFactory

    operation = 'updateDatastoreMetadata'
    statement = '''
    mutation UpdateDatastoreMetadata(
      $id: ID!,
      $name: String,
      $tags: [String],
      $isEnabled: Boolean
    ) {
      updateDatastoreMetadata(input: {
        id: $id,
        name: $name,
        tags: $tags,
        isEnabled: $isEnabled,
      }) {
        datastore {
          id
          name
          tags
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

        self.resource_kwargs = {
            'workspace': self.workspace,
            'name': 'Product Database',
            'tags': ['one', 'two', 'three'],
        }

        self.resource = self.factory(**self.resource_kwargs)
        self.global_id = helpers.to_global_id('DatastoreType', self.resource.pk)

    def execute_success_test_case(self):
        """It should permanently updates the datastore.
        """
        variables = {
            'id': self.global_id,
            'name': 'Data Warehouse',
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'id': self.global_id,
                'name': variables['name'],
                'tags': self.resource_kwargs['tags'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(self.resource, name=variables['name'])
        self.assertInstanceCreated(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should permanently updates the datastore.
        """
        self.execute_success_test_case()

    @decorators.as_someone(['OWNER'])
    def test_valid_with_object_permission_as_owner(self):
        """It should update the datastore.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()

        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission_as_member(self):
        """It should update the column when the user has the proper permissions.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()

        self.resource.assign_perm(self.user, 'definitions.change_datastore_settings')

        self.execute_success_test_case()

    @decorators.as_someone(['READONLY'])
    def test_invalid_with_object_permission_as_readonly(self):
        """It should return a "Permission Denied" error.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()
        self.resource.assign_perm(self.user, 'definitions.change_datastore_settings')

        variables = {
            'id': self.global_id,
            'name': 'Data Warehouse',
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceNotUpdated(self.resource, name=variables['name'])

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()

        variables = {
            'id': self.global_id,
            'name': 'Data Warehouse',
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceNotUpdated(self.resource, name=variables['name'])

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'id': self.global_id,
            'name': 'Data Warehouse',
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)


class DisableDatastoreCustomFieldsTests(cases.GraphQLTestCase):
    """Tests disabling certain custom fields.
    """
    load_data = ['workspaces.json', 'users.json', 'customfields.json']

    factory = factories.DatastoreFactory

    operation = 'disableDatastoreCustomFields'
    statement = '''
    mutation DisableDatastoreCustomFields(
      $id: ID!,
      $disabledDatastoreProperties: [String],
      $disabledTableProperties: [String],
    ) {
      disableDatastoreCustomFields(input: {
        id: $id,
        disabledDatastoreProperties: $disabledDatastoreProperties,
        disabledTableProperties: $disabledTableProperties,
      }) {
        datastore {
          id
          disabledDatastoreProperties
          disabledTableProperties
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def execute_success_test_case(self, resource):
        """It should update the datastore.
        """
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        d_customfield = self.workspace.custom_fields.filter(
            content_type__model="datastore",
        ).first()

        t_customfield = self.workspace.custom_fields.filter(
            content_type__model="table",
        ).first()

        variables = {
            'id': globalid,
            'disabledDatastoreProperties': [
                d_customfield.pk,
            ],
            'disabledTableProperties': [
                t_customfield.pk,
            ],
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'id': globalid,
                'disabledDatastoreProperties': variables['disabledDatastoreProperties'],
                'disabledTableProperties': variables['disabledTableProperties'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            resource,
            disabled_datastore_properties=variables['disabledDatastoreProperties'],
            disable_table_properties=variables['disabledTableProperties'],
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated allowed properties',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should update the datastore.
        """
        resource = self.factory(workspace=self.workspace)

        self.execute_success_test_case(resource)

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should update the datastore.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        resource.assign_perm(self.user, 'definitions.change_datastore_settings')

        self.execute_success_test_case(resource)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_with_fake_custom_field(self):
        """It should save without the fake field.
        """
        resource = resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        t_customfield = self.workspace.custom_fields.filter(
            content_type__model="table",
        ).first()

        variables = {
            'id': globalid,
            'disabledTableProperties': [
                t_customfield.pk,
                "abcdefghijklmnop",
            ],
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'id': globalid,
                'disabledDatastoreProperties': [],
                'disabledTableProperties': [t_customfield.pk],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            resource,
            disable_table_properties=[t_customfield.pk],
        )

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a "Permission Denied" error.
        """
        resource = resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        variables = {
            'id': globalid,
            'disabledDatastoreProperties': [],
            'disabledTableProperties': [],
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        variables = {
            'id': globalid,
            'disabledDatastoreProperties': [],
            'disabledTableProperties': [],
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)


class UpdateDatastoreJdbcConnectionTests(cases.GraphQLTestCase):
    """Tests for updating a datastore.
    """
    factory = factories.DatastoreFactory

    operation = 'updateDatastoreJdbcConnection'
    statement = '''
    mutation UpdateDatastoreJdbcConnection(
      $id: ID!,
      $username: String,
      $password: String,
      $database: String,
      $host: String,
      $port: Int,
      $sshEnabled: Boolean,
      $sshHost: String,
      $sshUser: String,
      $sshPort: Int,
    ) {
      updateDatastoreJdbcConnection(input: {
        id: $id,
        username: $username,
        password: $password,
        database: $database,
        host: $host,
        port: $port,
        sshEnabled: $sshEnabled,
        sshHost: $sshHost,
        sshUser: $sshUser,
        sshPort: $sshPort,
      }) {
        datastore {
          id
          jdbcConnection {
            engine
            host
            username
            database
            port
          }
          sshConfig {
            isEnabled
            host
            user
            port
          }
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

        self.resource_kwargs = {
            'workspace': self.workspace,
            'name': 'Product Database',
            'engine': random.choice(['oracle', 'postgresql', 'sqlserver']),
            'username': 'admin',
            'password': 'password1234',
            'database': 'product_db',
            'host': 'web-86.cortez.net',
            'port': 5439,
        }

        self.resource = self.factory(**self.resource_kwargs)
        self.global_id = helpers.to_global_id('DatastoreType', self.resource.pk)

    def execute_success_test_case(self):
        """It should permanently updates the datastore.
        """
        variables = {
            'id': self.global_id,
            'port': 5432,
            'username': 'Allison'
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': {
                'id': self.global_id,
                'jdbcConnection': {
                    'engine': self.resource.engine,
                    'host': self.resource_kwargs['host'],
                    'username': variables['username'],
                    'database': self.resource_kwargs['database'],
                    'port': variables['port'],
                },
                'sshConfig': {
                    'isEnabled': self.resource.ssh_enabled,
                    'host': self.resource.ssh_host,
                    'user': self.resource.ssh_user,
                    'port': self.resource.ssh_port,
                }
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=self.resource,
            username=variables['username'],
            port=variables['port'],
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self, mock_verify_connection):
        """It should updates the datastore.
        """
        self.execute_success_test_case()

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self, mock_verify_connection):
        """It should update the datastore connection.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()

        self.resource.assign_perm(self.user, 'definitions.change_datastore_connection')

        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.resource.object_permissions_enabled = True
        self.resource.save()

        variables = {
            'id': self.global_id,
            'port': 5432,
            'username': 'Allison'
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceNotUpdated(self.resource, username=variables['username'])

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid(self):
        """It should update the datastore.
        """
        variables = {
            'id': self.global_id,
            'port': -4000,
            'host': '',
            'username': ''.join(['a' for i in range(512)]),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'datastore': None,
            'errors': [
                {
                    'resource': 'Datastore',
                    'field': 'username',
                    'code': 'max_length',
                },
                {
                    'resource': 'Datastore',
                    'field': 'port',
                    'code': 'min_value',
                },
            ]
        })

        self.assertInstanceNotUpdated(
            instance=self.resource,
            host=variables['host'],
            username=variables['username'],
            port=variables['port'],
        )

        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    def test_not_found(self):
        variables = {
            'id': helpers.to_global_id('DatastoreType', '12345'),
            'port': 5432,
        }

        self.assertPermissionDenied(self.execute(variables=variables))

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        variables = {
            'id': self.global_id,
            'port': 5432,
            'username': 'Allison'
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class UpdateDatastoreAccessPrivilegesTests(cases.GraphQLTestCase):
    """Tests for removing a datastore.
    """
    factory = factories.DatastoreFactory

    operation = 'updateDatastoreAccessPrivileges'
    statement = '''
    mutation UpdateDatastoreAccessPrivileges($id: ID!, $objectId: ID!, $privileges: [String]!) {
      updateDatastoreAccessPrivileges(input: {
        id: $id,
        objectId: $objectId,
        privileges: $privileges,
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
    def test_valid_as_owner(self):
        """It should update permissions on an object.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)

        did = helpers.to_global_id('DatastoreType', resource.pk)
        oid = helpers.to_global_id('UserType', self.user.pk)

        privileges = [
            'view_datastore',
            'change_datastore_metadata',
            'change_datastore_settings',
            'change_datastore_connection',
            'delete_datastore',
        ]

        response = self.execute(variables={'id': did, 'objectId': oid, 'privileges': privileges})
        response = response['data'][self.operation]

        self.assertOk(response)
        for privilege in privileges:
            self.assertTrue(self.user.has_perm(privilege, resource))

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated access privileges to',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_user_object_permission(self):
        """It should update permissions on an object.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        resource.assign_perm(self.user, 'change_datastore_access')

        did = helpers.to_global_id('DatastoreType', resource.pk)
        oid = helpers.to_global_id('UserType', self.users['OWNER'].pk)

        privileges = [
            'view_datastore',
            'change_datastore_metadata',
            'change_datastore_settings',
            'change_datastore_connection',
            'delete_datastore',
        ]

        response = self.execute(variables={'id': did, 'objectId': oid, 'privileges': privileges})
        response = response['data'][self.operation]

        self.assertOk(response)
        for privilege in privileges:
            self.assertTrue(self.users['OWNER'].has_perm(privilege, resource))

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated access privileges to',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['OWNER'])
    def test_valid_with_group_object_permission(self):
        """It should update permissions on an object.
        """
        group = factories.GroupFactory(workspace_id=self.workspace.id)
        group.user_set.add(self.users['MEMBER'])

        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        resource.assign_perm(group, 'change_datastore_access')

        did = helpers.to_global_id('DatastoreType', resource.pk)
        oid = helpers.to_global_id('GroupType', group.pk)

        privileges = [
            'view_datastore',
            'change_datastore',
            'change_datastore_access',
        ]

        response = self.execute(variables={'id': did, 'objectId': oid, 'privileges': privileges})
        response = response['data'][self.operation]

        self.assertOk(response)
        for privilege in privileges:
            self.assertTrue(self.users['MEMBER'].has_perm(privilege, resource))

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated access privileges to',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)

        did = helpers.to_global_id('DatastoreType', resource.pk)
        oid = helpers.to_global_id('UserType', self.users['MEMBER'].pk)

        privileges = [
            'view_datastore',
            'change_datastore_metadata',
            'change_datastore_settings',
            'change_datastore_connection',
            'delete_datastore',
        ]

        response = self.execute(variables={
            'id': did,
            'objectId': oid,
            'privileges': privileges,
        })

        self.assertPermissionDenied(response)
        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='updated access privileges to',
            **serializers.get_audit_kwargs(resource),
        )


class ToggleDatastoreObjectPermissionsTests(cases.GraphQLTestCase):
    """Tests for removing a datastore.
    """
    factory = factories.DatastoreFactory

    operation = 'toggleDatastoreObjectPermissions'
    statement = '''
    mutation ToggleDatastoreObjectPermissions(
      $id: ID!
    ) {
      toggleDatastoreObjectPermissions(
        input: {
          id: $id
        }
      ) {
        isEnabled
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['OWNER'])
    def test_enabled(self):
        """It should permanently delete the datastore.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=False)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'isEnabled': True,
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            object_permissions_enabled=True,
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='enabled limited access to',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER'])
    def test_disabled_with_object_permissions(self):
        """It should permanently delete the datastore.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        resource.assign_perm(self.user, 'change_datastore_access')

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'isEnabled': False,
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=resource,
            object_permissions_enabled=False,
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='disabled limited access to',
            **serializers.get_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace, object_permissions_enabled=False)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)
        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)
        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='enabled limited access to',
            **serializers.get_audit_kwargs(resource),
        )


class DeleteDatastoreTests(cases.GraphQLTestCase):
    """Tests for removing a datastore.
    """
    factory = factories.DatastoreFactory

    operation = 'deleteDatastore'
    statement = '''
    mutation DeleteDatastore($id: ID!) {
      deleteDatastore(input: {
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

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should permanently delete the datastore.
        """
        resource = self.factory(workspace=self.workspace)
        global_id = helpers.to_global_id('DatastoreType', resource.pk)

        response = self.execute(variables={'id': global_id})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.Datastore,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)
        response = self.execute(variables={'id': globalid})
        self.assertPermissionDenied(response)

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        global_id = helpers.to_global_id('DatastoreType', '12345')

        response = self.execute(variables={'id': global_id})

        self.assertPermissionDenied(response)


class UpdateTableMetadataTests(cases.GraphQLTestCase):
    """Tests for updating table metadata.
    """
    factory = factories.TableFactory

    operation = 'updateTableMetadata'
    statement = '''
    mutation UpdateTableMetadata(
      $id: ID!,
      $tags: [String],
      $shortDesc: String,
    ) {
      updateTableMetadata(input: {
        id: $id,
        tags: $tags,
        shortDesc: $shortDesc,
      }) {
        table {
          id
          name
          tags
          shortDesc
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

        self.resource_kwargs = {
            'name': 'accounts',
            'tags': ['one', 'two'],
            'short_desc': 'This is a test.',
            'workspace': self.workspace,
        }

        self.resource = self.factory(**self.resource_kwargs)
        self.global_id = helpers.to_global_id('TableType', self.resource.pk)
        self.datastore = self.resource.datastore

    def execute_success_test_case(self):
        """It should update the table.
        """
        variables = {
            'id': self.global_id,
            'tags': [],
            'shortDesc': 'Hello, is it me you are looking for?'
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'table': {
                'id': self.global_id,
                'name': 'accounts',
                'tags': [],
                'shortDesc': variables['shortDesc'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=self.resource,
            tags=variables['tags'],
            short_desc=variables['shortDesc'],
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should update the table.
        """
        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should update the table when the user has the proper permissions.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.datastore.assign_perm(self.user, 'definitions.change_datastore_metadata')

        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_blank(self):
        """It should update the table.
        """
        variables = {
            'id': self.global_id,
            'tags': ['one'],
            'shortDesc': ''
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'table': {
                'id': self.global_id,
                'name': 'accounts',
                'tags': ['one'],
                'shortDesc': variables['shortDesc'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=self.resource,
            tags=variables['tags'],
            short_desc=variables['shortDesc'],
        )

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        # It still doesn't work of the user has similar permissions.
        self.datastore.assign_perm(self.user, 'definitions.change_datastore_settings')

        variables = {
            'id': self.global_id,
            'shortDesc': 'Hello, is it me you are looking for?'
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceNotUpdated(self.resource, short_desc=variables['shortDesc'])

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid(self):
        """It should not update the table.
        """
        variables = {
            'id': self.global_id,
            'shortDesc': ''.join(['a' for i in range(512)]),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'table': None,
            'errors': [
                {
                    'resource': 'Table',
                    'field': 'short_desc',
                    'code': 'max_length',
                },
            ]
        })

        self.assertInstanceNotUpdated(
            instance=self.resource,
            short_desc=variables['shortDesc'],
        )

        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'id': self.global_id,
            'tags': ['one'],
            'shortDesc': 'This is a test',
        }

        self.assertPermissionDenied(self.execute(variables=variables))
        self.assertInstanceNotUpdated(self.resource, short_desc=variables['shortDesc'])


class UpdateColumnMetadata(cases.GraphQLTestCase):
    """Tests for updating table metadata.
    """
    factory = factories.ColumnFactory

    operation = 'updateColumnMetadata'
    statement = '''
    mutation UpdateColumnMetadata(
      $id: ID!,
      $shortDesc: String,
    ) {
      updateColumnMetadata(input: {
        id: $id,
        shortDesc: $shortDesc,
      }) {
        column {
          id
          name
          shortDesc
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

        self.resource_kwargs = {
            'name': 'accounts',
            'short_desc': '',
            'workspace': self.workspace,
        }

        self.resource = self.factory(**self.resource_kwargs)
        self.global_id = helpers.to_global_id('ColumnType', self.resource.pk)
        self.datastore = self.resource.datastore

    def execute_success_test_case(self):
        """It should update the column.
        """
        variables = {
            'id': self.global_id,
            'shortDesc': 'Hello, is it me you are looking for?'
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'column': {
                'id': self.global_id,
                'name': 'accounts',
                'shortDesc': variables['shortDesc'],
            },
            'errors': None,
        })

        self.assertInstanceUpdated(
            instance=self.resource,
            short_desc=variables['shortDesc'],
        )

        self.assertInstanceCreated(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should update the column.
        """
        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should update the column when the user has the proper permissions.
        """
        self.datastore.datobject_permissions_enabled = True
        self.datastore.save()

        self.datastore.assign_perm(self.user, 'definitions.change_datastore_metadata')

        self.execute_success_test_case()

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        variables = {
            'id': self.global_id,
            'shortDesc': 'Hello, is it me you are looking for?'
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)
        self.assertInstanceNotUpdated(self.resource, short_desc=variables['shortDesc'])

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid(self):
        """It should not update the column.
        """
        variables = {
            'id': self.global_id,
            'shortDesc': ''.join(['a' for i in range(512)]),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'column': None,
            'errors': [
                {
                    'resource': 'Column',
                    'field': 'short_desc',
                    'code': 'max_length',
                },
            ]
        })

        self.assertInstanceNotUpdated(
            instance=self.resource,
            short_desc=variables['shortDesc'],
        )

        self.assertInstanceDoesNotExist(
            audit.Activity,
            verb='updated',
            **serializers.get_audit_kwargs(self.resource),
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'id': self.global_id,
            'shortDesc': 'This is a test',
        }

        self.assertPermissionDenied(self.execute(variables=variables))
        self.assertInstanceNotUpdated(self.resource, short_desc=variables['shortDesc'])


class TestJdbcConnectionTests(cases.GraphQLTestCase):
    """Tests for testing a jdbc connection.
    """
    factory = factories.DatastoreFactory

    operation = 'testJdbcConnection'
    statement = '''
    mutation TestJdbcConnection(
      $engine: String!,
      $username: String!,
      $password: String!,
      $database: String!,
      $host: String!,
      $port: Int!,
      $sshHost: String,
      $sshUser: String,
      $sshPort: Int,
    ) {
      testJdbcConnection(input: {
        engine: $engine,
        username: $username,
        password: $password,
        database: $database,
        host: $host,
        port: $port,
        sshHost: $sshHost,
        sshUser: $sshUser,
        sshPort: $sshPort,
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

    connection = {
        'engine': models.Datastore.POSTGRESQL,
        'username': 'postgres',
        'password': 'postgres',
        'database': 'metamapper',
        'host': 'database',
        'port': 5432,
    }

    @mock.patch.object(inspector, 'verify_connection', return_value=True)
    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self, mock_verify_connection):
        """It should update the table.
        """
        response = self.execute(variables=self.connection)
        response = response['data'][self.operation]

        self.assertOk(response)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    @mock.patch.object(inspector, 'verify_connection', return_value=False)
    def test_invalid(self, mock_verify_connection):
        """It should update the table.
        """
        response = self.execute(variables=self.connection)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': False,
            'errors': [
                {
                    'resource': 'Datastore',
                    'field': 'jdbc_connection',
                    'code': 'invalid',
                },
            ]
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    @mock.patch.object(inspector, 'verify_connection', return_value=False)
    def test_unauthorized(self, mock_verify_connection):
        """It should return a "Permission Denied" error.
        """
        self.assertPermissionDenied(self.execute(variables=self.connection))


class TestCreateAssetOwner(cases.GraphQLTestCase):
    """Tests for creating a table owner.
    """
    operation = 'createAssetOwner'
    statement = '''
    mutation CreateAssetOwner(
      $objectId: ID!
      $ownerId: ID!
      $order: Int
    ) {
      createAssetOwner(input: {
        objectId: $objectId,
        ownerId: $ownerId,
        order: $order,
      }) {
        assetOwner {
          type
          owner {
            id
            name
          }
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

        self.resource = factories.TableFactory(name='accounts', workspace=self.workspace)
        self.datastore = self.resource.datastore
        self.object_id = helpers.to_global_id('TableType', self.resource.pk)

    def execute_success_test_case(self, owner_type, owner):
        """It should create the data asset owner.
        """
        variables = {
            'objectId': self.object_id,
            'ownerId': helpers.to_global_id(owner_type, owner.id),
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'assetOwner': {
                'type': owner.__class__.__name__.upper(),
                'owner': {
                    'id': variables['ownerId'],
                    'name': owner.name,
                },
            },
            'errors': None
        })

        resource = models.AssetOwner.objects.get(owner_id=owner.id, object_id=self.resource.id)

        self.assertInstanceCreated(
            audit.Activity,
            verb='created',
            **serializers.get_asset_owner_audit_kwargs(resource),
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_with_valid_user(self):
        """It should create the asset owner when the user has the proper permissions.
        """
        self.execute_success_test_case('UserType', self.user)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_with_valid_group(self):
        """It should create the asset owner when the user has the proper permissions.
        """
        self.execute_success_test_case('GroupType', factories.GroupFactory(workspace=self.workspace))

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should create the asset owner when the user has the proper permissions.
        """
        self.datastore.datobject_permissions_enabled = True
        self.datastore.save()

        self.datastore.assign_perm(self.user, 'definitions.change_datastore_metadata')

        self.execute_success_test_case('UserType', self.user)

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        variables = {
            'objectId': self.object_id,
            'ownerId': helpers.to_global_id('UserType', self.user.id),
        }

        response = self.execute(variables=variables)

        self.assertPermissionDenied(response)

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'objectId': self.object_id,
            'ownerId': helpers.to_global_id('UserType', self.user.id),
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class TestUpdateAssetOwner(cases.GraphQLTestCase):
    """Tests for creating a table owner.
    """
    operation = 'updateAssetOwner'
    statement = '''
    mutation UpdateAssetOwner(
      $id: ID!
      $order: Int!
    ) {
      updateAssetOwner(input: {
        id: $id,
        order: $order,
      }) {
        assetOwner {
          type
          order
          owner {
            name
          }
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
        self.resource = factories.TableFactory(name='accounts', workspace=self.workspace)

        self.resource.owners.create(workspace=self.workspace, owner=self.users['READONLY'])
        self.resource.owners.create(workspace=self.workspace, owner=self.users['OWNER'])
        self.asset_owner = self.resource.owners.create(workspace=self.workspace, owner=self.users['MEMBER'])

        self.global_id = helpers.to_global_id('AssetOwnerType', self.asset_owner.id)
        self.datastore = self.resource.datastore

    def execute_success_test_case(self, owner_type, owner, order):
        """It should create the data asset owner.
        """
        variables = {
            'id': helpers.to_global_id(owner_type, owner.id),
            'order': order,
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        owner_instance = owner.owner

        self.assertEqual(response, {
            'assetOwner': {
                'type': owner_instance.__class__.__name__.upper(),
                'order': order,
                'owner': {
                    'name': owner_instance.name,
                },
            },
            'errors': None
        })

        self.assertInstanceUpdated(self.asset_owner, order=order)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should create the asset owner when the user has the proper permissions.
        """
        self.execute_success_test_case('AssetOwnerType', self.asset_owner, 2)

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should create the asset owner when the user has the proper permissions.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        self.datastore.assign_perm(self.user, 'definitions.change_datastore_metadata')

        self.execute_success_test_case('AssetOwnerType', self.asset_owner, 2)

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        variables = {
            'id': self.global_id,
            'order': 1,
        }

        response = self.execute(variables=variables)
        self.assertPermissionDenied(response)

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        variables = {
            'id': self.global_id,
            'order': 1,
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class TestDeleteAssetOwner(cases.GraphQLTestCase):
    """Tests for deleting an asset owner.
    """
    operation = 'deleteAssetOwner'
    statement = '''
    mutation DeleteAssetOwner($id: ID!) {
      deleteAssetOwner(input: {
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

    def setUp(self):
        super().setUp()

        self.resource = factories.TableFactory(workspace=self.workspace)
        self.datastore = self.resource.datastore

    def execute_success_test_case(self, owner):
        """It should create the data asset owner.
        """
        node_id = helpers.to_global_id('AssetOwnerType', owner.pk)

        response = self.execute(variables={'id': node_id})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceCreated(models.AssetOwner, id=owner.id, workspace_id=self.workspace.id)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should delete the asset owner when the user has the proper permissions.
        """
        owner = self.resource.owners.create(workspace=self.workspace, owner=self.user)

        self.execute_success_test_case(owner)

    @decorators.as_someone(['MEMBER'])
    def test_valid_with_object_permission(self):
        """It should delete the asset owner when the user has the proper permissions.
        """
        self.datastore.datobject_permissions_enabled = True
        self.datastore.save()

        self.datastore.assign_perm(self.user, 'definitions.change_datastore_metadata')
        owner = self.resource.owners.create(workspace=self.workspace, owner=self.user)

        self.execute_success_test_case(owner)

    @decorators.as_someone(['MEMBER'])
    def test_invalid_without_object_permission(self):
        """It should return a Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        owner = self.resource.owners.create(workspace=self.workspace, owner=self.user)

        node_id = helpers.to_global_id('AssetOwnerType', owner.pk)
        response = self.execute(variables={'id': node_id})

        self.assertPermissionDenied(response)

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        owner = self.resource.owners.create(workspace=self.workspace, owner=self.user)
        node_id = helpers.to_global_id('AssetOwnerType', owner.pk)

        self.assertPermissionDenied(self.execute(variables={'id': node_id}))

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        self.assertPermissionDenied(self.execute(variables={'id': helpers.to_global_id('AssetOwnerType', '12345')}))
