# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class TestGetRunHistory(cases.GraphQLTestCase):
    """Test cases for listing revisions related to a datastore.
    """
    factory = factories.RevisionerRunFactory
    operation = 'runHistory'
    statement = '''
    query getRunHistory($datastoreId: ID!) {
      runHistory(
        datastoreId: $datastoreId
      ) {
        edges {
          node {
            id
            pk
            status
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetRunHistory, self).setUp()

        self.count = 5
        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.global_id = helpers.to_global_id('DatastoreType', self.datastore.pk)
        self.runs = self.factory.create_batch(self.count, datastore=self.datastore)
        self.other_datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.other_run = self.factory(datastore=self.other_datastore)

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'datastoreId': self.global_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of active runs for this datastore."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'datastoreId': self.global_id})
        )

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_when_not_logged_in(self):
        """Outside users should not be able to access this resource.
        """
        self.assertNotFound(
            self.execute(self.statement, variables={'datastoreId': self.global_id})
        )
