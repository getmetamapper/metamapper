# -*- coding: utf-8 -*-
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

        self.count = 5
        self.datastores = self.factory.create_batch(self.count, workspace=self.workspace)
        self.other_datastore = self.factory(workspace=self.other_workspace)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count + 1,
            msg="Node count should equal number of active datastores."
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

    def test_query(self):
        """It should return a limited number of datastores.
        """
        results = self.execute(self.statement, variables={'search': 'alpha'})
        results = results['data'][self.operation]

        self.assertEqual(len(results['edges']), 2)
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

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'id': self.global_id})
        self.assertPermissionDenied(results)
