# -*- coding: utf-8 -*-
import unittest.mock as mock

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class QueueRevisionerRunTests(cases.GraphQLTestCase):
    """Tests for manually queueing a revisioner run.
    """
    operation = 'queueRevisionerRun'
    statement = '''
    mutation QueueRevisionerRun(
      $datastoreId: ID!,
    ) {
      queueRevisionerRun(datastoreId: $datastoreId) {
        ok
      }
    }
    '''

    def setUp(self):
        super().setUp()
        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.datastore_id = helpers.to_global_id('DatastoreType', self.datastore.id)

    @mock.patch('app.revisioner.tasks.v1.scheduler.create_runs')
    @mock.patch('app.revisioner.tasks.v1.scheduler.queue_runs')
    @decorators.as_someone(['OWNER'])
    def test_valid(self, queue_runs, create_runs):
        """It should create a ApiToken scoped to Workspace.
        """
        create_runs.return_value = [1, 2, 3]

        response = self.execute(variables={'datastoreId': self.datastore_id})
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'ok': True,
        })

        create_runs.assert_called_with(datastore_slug=self.datastore.slug)
        queue_runs.assert_called_with(self.datastore.slug, countdown_in_minutes=0)

    @decorators.as_someone(['READONLY', 'MEMBER', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(variables={'datastoreId': self.datastore_id}))
