# -*- coding: utf-8 -*-
import unittest.mock as mock
import app.definitions.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class TestGetDatastores(cases.GraphQLTestCase):
    """Test cases for listing all datastores in a workspace.
    """
    factory = factories.DatastoreFactory
    operation = 'datastores'
    statement = '''
    query getDatastores {
      datastores {
        edges {
          node {
            id
            pk
            name
            isEnabled
            jdbcConnection {
              engine
            }
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetDatastores, self).setUp()

        models.Datastore.objects.all().delete()

        self.count = 5
        self.datastores = self.factory.create_batch(self.count, workspace=self.workspace)
        self.other_datastore = self.factory(workspace=self.other_workspace)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of active datastores."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_object_permissions_are_disabled(self):
        restricted_datastore = self.factory(workspace=self.workspace, object_permissions_enabled=True)

        results = self.execute(self.statement)
        results = results['data'][self.operation]

        count = self.count

        # Owners should still be able to see every datastore in the workspace.
        if self.user_type == 'OWNER':
            count += 1

        self.assertEqual(
            first=len(results['edges']),
            second=count,
            msg="Node count should equal number of active datastores."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

        # We need to clean up this test at the end so it doesn't affect the other decorated tests.
        restricted_datastore.delete()

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))


class TestSearchDatastoresByName(cases.GraphQLTestCase):
    """Test cases for searching for a datastore.
    """
    factory = factories.DatastoreFactory
    operation = 'datastores'
    statement = '''
    query getDatastores($search: String) {
      datastores(search: $search) {
        edges {
          node {
            name
            isEnabled
          }
        }
      }
    }
    '''

    def setUp(self):
        super(TestSearchDatastoresByName, self).setUp()

        self.names = [
            'Alpha',
            'Beta',
            'Alpha Beta',
        ]

        self.datastores = []

        for n in self.names:
            self.datastores.append(
                self.factory(name=n, workspace=self.workspace)
            )

        self.excluded_datastore = self.factory(
            name='Beta Alpha',
            workspace=self.workspace,
            object_permissions_enabled=True,
        )

        self.names += ['Beta Alpha']

    def test_query(self):
        """It should return a limited number of datastores.
        """
        results = self.execute(self.statement, variables={'search': 'alpha'})
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), 3)
        self.assertIn(results['edges'][0]['node']['name'], self.names)

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permissions_filters(self):
        """It should return a limited number of datastores.
        """
        results = self.execute(self.statement, variables={'search': 'alpha'})
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), 2)
        self.assertIn(results['edges'][0]['node']['name'], self.names)

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_with_object_permission_granted(self):
        """It should return a limited number of datastores.
        """
        self.excluded_datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables={'search': 'alpha'})
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), 3)
        self.assertIn(results['edges'][0]['node']['name'], self.names)


class TestGetDatastore(cases.GraphQLTestCase):
    """Test cases for fetching a specific datastore.
    """
    factory = factories.DatastoreFactory
    operation = 'datastore'
    statement = '''
    query getDatastoreSettings($id: ID!) {
      datastore(id: $id) {
        name
        tags
        version
        isEnabled
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
          publicKey
        }
      }
    }
    '''

    def setUp(self):
        super(TestGetDatastore, self).setUp()

        self.datastore_kwargs = {
            'name': 'Metamapper',
            'tags': ['metadata', 'platform'],
            'version': '9.0.1',
            'is_enabled': False,
            'engine': 'mysql',
            'host': 'locahost',
            'username': 'admin',
            'password': 'password1234',
            'port': 3306,
            'database': 'metadata',
            'workspace': self.workspace,
            'ssh_host': '127.0.0.1',
            'ssh_user': 'ubuntu',
            'ssh_port': 22,
        }

        self.datastore = self.factory(**self.datastore_kwargs)
        self.global_id = helpers.to_global_id('DatastoreType', self.datastore.pk)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It should return the requested resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': 'Metamapper',
            'tags': ['metadata', 'platform'],
            'version': '9.0.1',
            'isEnabled': False,
            'jdbcConnection': {
                'engine': 'mysql',
                'host': 'locahost',
                'username': 'admin',
                'database': 'metadata',
                'port': 3306,
            },
            'sshConfig': {
                'isEnabled': False,
                'host': '127.0.0.1',
                'user': 'ubuntu',
                'port': 22,
                'publicKey': self.workspace.ssh_public_key,
            }
        })

    @decorators.as_someone(['OWNER'])
    def test_object_permissions_as_owner(self):
        """It should return the requested resource if object-level permissions are granted.
        """
        datastore = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        global_id = helpers.to_global_id('DatastoreType', datastore.pk)

        results = self.execute(self.statement, variables={'id': global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': datastore.name,
            'tags': datastore.tags,
            'version': datastore.version,
            'isEnabled': datastore.is_enabled,
            'jdbcConnection': {
                'engine': datastore.engine,
                'host': datastore.host,
                'username': datastore.username,
                'database': datastore.database,
                'port': datastore.port,
            },
            'sshConfig': {
                'isEnabled': datastore.ssh_enabled,
                'host': datastore.ssh_host,
                'user': datastore.ssh_user,
                'port': datastore.ssh_port,
                'publicKey': self.workspace.ssh_public_key,
            }
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_object_permissions(self):
        """It should return the requested resource if object-level permissions are granted.
        """
        datastore = self.factory(workspace=self.workspace, object_permissions_enabled=True)
        global_id = helpers.to_global_id('DatastoreType', datastore.pk)

        results = self.execute(self.statement, variables={'id': global_id})

        self.assertPermissionDenied(results)

        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables={'id': global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': datastore.name,
            'tags': datastore.tags,
            'version': datastore.version,
            'isEnabled': datastore.is_enabled,
            'jdbcConnection': {
                'engine': datastore.engine,
                'host': datastore.host,
                'username': datastore.username,
                'database': datastore.database,
                'port': datastore.port,
            },
            'sshConfig': {
                'isEnabled': datastore.ssh_enabled,
                'host': datastore.ssh_host,
                'user': datastore.ssh_user,
                'port': datastore.ssh_port,
                'publicKey': self.workspace.ssh_public_key,
            }
        })

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        self.assertPermissionDenied(results)


class TestGetDatastoreBySlug(cases.GraphQLTestCase):
    """Tests for getting a datastore by slug.
    """
    factory = factories.DatastoreFactory
    operation = 'datastoreBySlug'
    statement = '''
    query getDatastoreBySlug($slug: String!) {
      datastoreBySlug(slug: $slug) {
        name
        isEnabled
      }
    }
    '''

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It returns the datastore object.
        """
        datastore = self.factory(workspace=self.workspace)

        results = self.execute(self.statement, variables={'slug': datastore.slug})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': datastore.name,
            'isEnabled': datastore.is_enabled,
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        datastore = self.factory(workspace=self.workspace, object_permissions_enabled=True)

        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables={'slug': datastore.slug})
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': datastore.name,
            'isEnabled': datastore.is_enabled,
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        datastore = self.factory(workspace=self.workspace, object_permissions_enabled=True)

        results = self.execute(self.statement, variables={'slug': datastore.slug})
        self.assertPermissionDenied(results)

    def test_not_found(self):
        """If the datastore does not exist, we return a 404 – Not Found message.
        """
        results = self.execute(self.statement, variables={'slug': 'hvob'})

        self.assertNotFound(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        datastore = self.factory(workspace=self.workspace)

        results = self.execute(self.statement, variables={'slug': datastore.slug})
        self.assertPermissionDenied(results)


class TestGetTableDefinition(cases.GraphQLTestCase):
    """Tests for getting a table definition for a datastore.
    """
    factory = factories.TableFactory
    operation = 'tableDefinition'
    statement = '''
    query getTableDefinition(
      $datastoreId: ID!
      $schemaName: String!
      $tableName: String!
    ) {
      tableDefinition(
        datastoreId: $datastoreId
        schemaName: $schemaName
        tableName: $tableName
      ) {
        name
        schema {
          name
        }
        owners {
          type
          owner {
            id
            name
          }
        }
      }
    }
    '''

    def _setup_and_get_variables(self, **overrides):
        """Setup test and return variables for query.
        """
        datastore = factories.DatastoreFactory(workspace=self.workspace, **overrides)
        schema = factories.SchemaFactory(workspace=self.workspace, datastore=datastore)

        table = self.factory(workspace=self.workspace, schema=schema)

        variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', datastore.pk),
            'schemaName': schema.name,
            'tableName': table.name,
        }

        return datastore, variables

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It returns the table definition object.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': variables['tableName'],
            'schema': {
                'name': variables['schemaName'],
            },
            'owners': [],
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        datastore, variables = self._setup_and_get_variables(object_permissions_enabled=True)
        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': variables['tableName'],
            'schema': {
                'name': variables['schemaName'],
            },
            'owners': [],
        })

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_with_owners(self):
        """It returns the table definition object with owners attached.
        """
        datastore, variables = self._setup_and_get_variables()

        table = datastore.schemas.first().tables.first()
        table.owners.create(owner=self.user, workspace=table.workspace)

        group = self.workspace.groups.get(id=12412)
        table.owners.create(owner=group, workspace=table.workspace)

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': variables['tableName'],
            'schema': {
                'name': variables['schemaName'],
            },
            'owners': [
                {
                    'owner': {
                        'id': helpers.to_global_id('UserType', self.user.id),
                        'name': self.user.name,
                    },
                    'type': 'USER',
                },
                {
                    'owner': {
                        'id': helpers.to_global_id('GroupType', group.id),
                        'name': group.name,
                    },
                    'type': 'GROUP',
                }
            ],
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        _, variables = self._setup_and_get_variables(object_permissions_enabled=True)

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)

    def test_not_found(self):
        """If the datastore does not exist, we return a 404 – Not Found message.
        """
        _, variables = self._setup_and_get_variables()
        variables.update({'tableName': 'not_real'})

        results = self.execute(self.statement, variables=variables)
        self.assertNotFound(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)


class TestGetColumnDefinition(cases.GraphQLTestCase):
    """Tests for getting a column definition for a datastore.
    """
    factory = factories.ColumnFactory
    operation = 'columnDefinition'
    statement = '''
    query GetColumnDefinition(
      $datastoreId: ID!
      $schemaName: String!
      $tableName: String!
      $columnName: String!
    ) {
      columnDefinition(
        datastoreId: $datastoreId
        schemaName: $schemaName
        tableName: $tableName
        columnName: $columnName
      ) {
        name
        readme
        table {
          name
        }
      }
    }
    '''

    readme = '''
    # Foobar

    Foobar is a Python library for dealing with word pluralization.

    ## Installation

    Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

    ```bash
    pip install foobar
    ```
    '''

    def _setup_and_get_variables(self, **overrides):
        """Setup test and return variables for query.
        """
        datastore = factories.DatastoreFactory(workspace=self.workspace, **overrides)
        schema = factories.SchemaFactory(workspace=self.workspace, datastore=datastore)
        table = factories.TableFactory(workspace=self.workspace, schema=schema)
        column = self.factory(workspace=self.workspace, table=table, readme=self.readme)

        variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', datastore.pk),
            'schemaName': schema.name,
            'tableName': table.name,
            'columnName': column.name,
        }

        return datastore, variables

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query(self):
        """It returns the table definition object.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': variables['columnName'],
            'readme': self.readme,
            'table': {
                'name': variables['tableName'],
            },
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        datastore, variables = self._setup_and_get_variables(object_permissions_enabled=True)
        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, {
            'name': variables['columnName'],
            'readme': self.readme,
            'table': {
                'name': variables['tableName'],
            },
        })

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        _, variables = self._setup_and_get_variables(object_permissions_enabled=True)

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)

    def test_not_found(self):
        """If the column does not exist, we return a 404 – Not Found message.
        """
        _, variables = self._setup_and_get_variables()
        variables.update({'tableName': 'not_real'})

        results = self.execute(self.statement, variables=variables)
        self.assertNotFound(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)


class TestGetDatastoreUserAccessPrivileges(cases.GraphQLTestCase):
    """Tests for getting datastore privileges scoped to users.
    """
    factory = factories.DatastoreFactory
    operation = 'datastoreUserAccessPrivileges'
    statement = '''
    query GetDatastoreAccessPrivileges($datastoreId: ID!) {
      datastoreUserAccessPrivileges(datastoreId: $datastoreId) {
        id
        name
        privileges
      }
    }
    '''

    def _setup_and_get_variables(self, **overrides):
        """Setup test and return variables for query.
        """
        datastore = factories.DatastoreFactory(workspace=self.workspace, **overrides)
        datastore.assign_all_perms(self.users['OWNER'])

        variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', datastore.pk),
        }

        return datastore, variables

    @decorators.as_someone(['OWNER'])
    def test_query(self):
        """It returns the table definition object.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {
                'id': 'VXNlclR5cGU6MQ==',
                'name': 'Sam Crust',
                'privileges': [
                    'add_datastore',
                    'change_datastore',
                    'change_datastore_access',
                    'change_datastore_connection',
                    'change_datastore_metadata',
                    'change_datastore_settings',
                    'comment_on_datastore',
                    'delete_datastore',
                    'view_datastore',
                ]
            }
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        datastore, variables = self._setup_and_get_variables(object_permissions_enabled=True)

        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {
                'id': 'VXNlclR5cGU6MQ==',
                'name': 'Sam Crust',
                'privileges': [
                    'add_datastore',
                    'change_datastore',
                    'change_datastore_access',
                    'change_datastore_connection',
                    'change_datastore_metadata',
                    'change_datastore_settings',
                    'comment_on_datastore',
                    'delete_datastore',
                    'view_datastore',
                ]
            },
            {
                'id': helpers.to_global_id('UserType', self.user.pk),
                'name': self.user.name,
                'privileges': [
                    'view_datastore',
                ]
            },
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        _, variables = self._setup_and_get_variables(object_permissions_enabled=True)

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)

    def test_not_found(self):
        """If the datastore does not exist, we return a 404 – Not Found message.
        """
        results = self.execute(self.statement, variables={
            'datastoreId': helpers.to_global_id('DatastoreType', '123456'),
        })
        self.assertNotFound(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)


class TestGetDatastoreGroupAccessPrivileges(cases.GraphQLTestCase):
    """Tests for getting datastore privileges scoped to groups.
    """
    factory = factories.DatastoreFactory
    operation = 'datastoreGroupAccessPrivileges'
    statement = '''
    query GetDatastoreAccessPrivileges($datastoreId: ID!) {
      datastoreGroupAccessPrivileges(datastoreId: $datastoreId) {
        id
        name
        privileges
      }
    }
    '''

    def setUp(self):
        super().setUp()
        self.group = factories.GroupFactory(workspace_id=self.workspace.id)
        self.other_group = factories.GroupFactory(workspace_id=self.workspace.id)
        self.outside_group = factories.GroupFactory(workspace_id=self.other_workspace.id)

    def _setup_and_get_variables(self, **overrides):
        """Setup test and return variables for query.
        """
        datastore = factories.DatastoreFactory(workspace=self.workspace, **overrides)
        datastore.assign_all_perms(self.group)

        variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', datastore.pk),
        }

        return datastore, variables

    @decorators.as_someone(['OWNER'])
    def test_query(self):
        """It returns the table definition object.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {
                'id': helpers.to_global_id('GroupType', self.group.pk),
                'name': self.group.name,
                'privileges': [
                    'add_datastore',
                    'change_datastore',
                    'change_datastore_access',
                    'change_datastore_connection',
                    'change_datastore_metadata',
                    'change_datastore_settings',
                    'comment_on_datastore',
                    'delete_datastore',
                    'view_datastore',
                ]
            }
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        self.group.user_set.add(self.user)

        datastore, variables = self._setup_and_get_variables(object_permissions_enabled=True)
        datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {
                'id': helpers.to_global_id('GroupType', self.group.pk),
                'name': self.group.name,
                'privileges': [
                    'add_datastore',
                    'change_datastore',
                    'change_datastore_access',
                    'change_datastore_connection',
                    'change_datastore_metadata',
                    'change_datastore_settings',
                    'comment_on_datastore',
                    'delete_datastore',
                    'view_datastore',
                ]
            }
        ])

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        _, variables = self._setup_and_get_variables(object_permissions_enabled=True)

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)

    def test_not_found(self):
        """If the datastore does not exist, we return a 404 – Not Found message.
        """
        results = self.execute(self.statement, variables={
            'datastoreId': helpers.to_global_id('DatastoreType', '123456'),
        })
        self.assertNotFound(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        _, variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        self.assertPermissionDenied(results)


class TestGetDatastoreAssets(cases.GraphQLTestCase):
    """Tests for retrieving a list of tables associated with a datastore.
    """
    factory = factories.DatastoreFactory
    operation = 'datastoreAssets'
    statement = '''
    query GetDatastoreAssets($datastoreSlug: String!, $schemaName: String, $search: String, $first: Int, $after: String) {
      datastoreAssets(
        slug: $datastoreSlug
        schema: $schemaName
        search: $search
        first: $first
        after: $after
      ) {
        edges {
          node {
            id
            name
            kind
            shortDesc
            schema {
              name
            }
          }
        }
        pageInfo {
          endCursor
          hasNextPage
        }
      }
    }
    '''

    def setUp(self):
        super(TestGetDatastoreAssets, self).setUp()

        self.datastore = self.factory(workspace=self.workspace)
        self.schema = factories.SchemaFactory(datastore=self.datastore)

        self.assets = []

        for i in range(10):
            self.assets.append(
                factories.TableFactory(name='app%s' % str(i).zfill(3), schema=self.schema)
            )

        for j in range(10):
            self.assets.append(
                factories.TableFactory(name='site%s' % str(j).zfill(3), schema=self.schema)
            )

        self.other_datastore = self.factory(workspace=self.workspace)
        self.other_schema = factories.SchemaFactory(datastore=self.other_datastore)
        self.other_table = factories.TableFactory(schema=self.other_schema, name='yyz')

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_valid(self):
        """Outside users should not be able to access this resource.
        """
        variables = {
            'datastoreSlug': self.datastore.slug,
            'first': 100,
        }

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(len(self.assets), len(results['edges']))

        names = []
        for edge in results['edges']:
            names.append(edge['node']['name'])

        for asset in self.assets:
            self.assertIn(asset.name, names)

        self.assertNotIn(self.other_table.name, names)

    def test_pagination(self):
        """It should implement cursor pagination.
        """
        variables = {
            'datastoreSlug': self.datastore.slug,
            'first': 10,
        }

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertTrue(results['pageInfo']['hasNextPage'])

        variables['after'] = results['pageInfo']['endCursor']

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertFalse(results['pageInfo']['hasNextPage'])

    def test_search(self):
        """It should implement cursor pagination.
        """
        variables = {
            'datastoreSlug': self.datastore.slug,
            'search': 'app',
        }

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), 10)

    def test_filter_by_schema(self):
        """It should filter the queryset by the provided schema.
        """
        schema = factories.SchemaFactory(datastore=self.datastore, name='public')
        tables = factories.TableFactory.create_batch(5, schema=schema)

        variables = {
            'datastoreSlug': self.datastore.slug,
            'schemaName': schema.name,
        }

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), len(tables))

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'datastoreSlug': self.datastore.slug})
        self.assertPermissionDenied(results)


class TestGetSchemaNamesByDatastore(cases.GraphQLTestCase):
    """Tests for getting a list of schema names for a datastore.
    """
    factory = factories.DatastoreFactory
    operation = 'schemaNamesByDatastore'
    statement = '''
    query GetDatastoreSchemaNames($datastoreId: ID!) {
        schemaNamesByDatastore(datastoreId: $datastoreId)
    }
    '''

    def setUp(self):
        super(TestGetSchemaNamesByDatastore, self).setUp()

        self.datastore = self.factory(workspace=self.workspace)
        self.schemas = factories.SchemaFactory.create_batch(10, datastore=self.datastore)

        self.other_schema = factories.SchemaFactory()

        self.variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', self.datastore.pk),
        }

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_valid(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables=self.variables)
        results = results['data'][self.operation]

        self.assertTrue(len(results), len(self.schemas))
        self.assertTrue(self.other_schema.name not in results)

        for schema in self.schemas:
            self.assertIn(schema.name, results)

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=self.variables)
        results = results['data'][self.operation]

        self.assertTrue(len(results), len(self.schemas))

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables=self.variables)
        self.assertPermissionDenied(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables=self.variables)
        self.assertPermissionDenied(results)


class TestGetTableNamesBySchema(cases.GraphQLTestCase):
    """Tests for getting datastore privileges scoped to groups.
    """
    factory = factories.DatastoreFactory
    operation = 'tableNamesBySchema'
    statement = '''
    query GetSchemaTableNames(
        $datastoreId: ID!
        $schemaName: String!
    ) {
        tableNamesBySchema(datastoreId: $datastoreId, schemaName: $schemaName)
    }
    '''

    def setUp(self):
        super(TestGetTableNamesBySchema, self).setUp()

        self.datastore = self.factory(workspace=self.workspace)
        self.schema = factories.SchemaFactory(datastore=self.datastore)
        self.tables = factories.TableFactory.create_batch(10, schema=self.schema)

        self.other_schema = factories.SchemaFactory(datastore=self.datastore)
        self.other_table = factories.TableFactory(schema=self.other_schema)

        self.variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', self.datastore.pk),
            'schemaName': self.schema.name,
        }

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_valid(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables=self.variables)
        results = results['data'][self.operation]

        self.assertTrue(len(results), len(self.tables))
        self.assertTrue(self.other_table.name not in results)

        for table in self.tables:
            self.assertIn(table.name, results)

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_with_object_permissions(self):
        """It returns the datastore object.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()
        self.datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute(self.statement, variables=self.variables)
        results = results['data'][self.operation]

        self.assertTrue(len(results), len(self.tables))

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_without_object_permissions(self):
        """It returns a 403 - Permission Denied error.
        """
        self.datastore.object_permissions_enabled = True
        self.datastore.save()

        results = self.execute(self.statement, variables=self.variables)
        self.assertPermissionDenied(results)

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables=self.variables)
        self.assertPermissionDenied(results)


class TestGetTableLastCommitTimestamp(cases.GraphQLTestCase):
    """Test cases for retrieving the last time a table was modified.
    """
    factory = factories.TableFactory
    operation = 'tableLastCommitTimestamp'
    statement = '''
    query GetTableLastCommitTimestamp(
      $datastoreId: ID!
      $schemaName: String!
      $tableName: String!
    ) {
      tableLastCommitTimestamp(
        datastoreId: $datastoreId
        schemaName: $schemaName
        tableName: $tableName
      )
    }
    '''

    def _setup_and_get_variables(self, **overrides):
        """Setup test and return variables for query.
        """
        datastore = factories.DatastoreFactory(workspace=self.workspace, **overrides)
        schema = factories.SchemaFactory(workspace=self.workspace, datastore=datastore)

        table = self.factory(workspace=self.workspace, schema=schema)

        variables = {
            'datastoreId': helpers.to_global_id('DatastoreType', datastore.pk),
            'schemaName': schema.name,
            'tableName': table.name,
        }

        return variables

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    @mock.patch('app.inspector.service.get_engine')
    def test_query_when_authorized(self, mock_get_engine):
        mocked = mock.MagicMock()
        mocked.get_last_commit_time_for_table.return_value = '2020-01-01'
        mock_get_engine.return_value = mocked

        variables = self._setup_and_get_variables()

        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]

        self.assertEqual(
            results,
            mocked.get_last_commit_time_for_table.return_value,
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        variables = self._setup_and_get_variables()
        self.assertPermissionDenied(self.execute(self.statement, variables=variables))
