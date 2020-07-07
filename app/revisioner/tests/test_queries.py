# -*- coding: utf-8 -*-
import uuid

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers

from app.definitions.models import Table
from app.revisioner.models import Run, Revision

from django.core.management import call_command


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
            revisionCount
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

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(
            self.execute(self.statement, variables={'datastoreId': self.global_id})
        )


class TestGetRunRevisions(cases.GraphQLTestCase):
    """Test cases for listing all datastores in a workspace.
    """
    load_data = [
        'workspaces.json',
        'users.json',
        'revisioner.json',
    ]

    run_id = '079d08c0-8c14-4c6f-90ee-ebc0b6c9b974'

    operation = 'runRevisions'
    statement = '''
    query getRunRevisions($runId: ID!) {
      runRevisions(
        runId: $runId,
      ) {
        edges {
          node {
            id
            action
            metadata
            appliedOn
            relatedResource {
              id
              pk
              type
              label
            }
          }
        }
        totalCount
      }
    }
    '''

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        """Test the query.
        """
        node_id = helpers.to_global_id('RunType', self.run_id)
        results = self.execute(self.statement, variables={'runId': node_id})
        results = results['data'][self.operation]

        run = Run.objects.get(pk=self.run_id)

        self.assertEqual(
            first=len(results['edges']),
            second=run.revision_count,
            msg="Node count should equal number of revisions."
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
        node_id = helpers.to_global_id('RunType', self.run_id)
        results = self.execute(self.statement, variables={'runId': node_id})

        self.assertPermissionDenied(results)

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_when_not_authenticated(self):
        """Outside users should not be able to access this resource.
        """
        node_id = helpers.to_global_id('RunType', self.run_id)
        results = self.execute(self.statement, variables={'runId': node_id})

        self.assertNotFound(results)


class TestGetTableRevisions(cases.GraphQLTestCase):
    """Test cases for listing all datastores in a workspace.
    """
    load_data = [
        'workspaces.json',
        'users.json',
        'revisioner.json',
    ]

    operation = 'tableRevisions'
    statement = '''
    query getTableObjectRevisions(
      $tableId: ID!,
    ) {
      tableRevisions(
        tableId: $tableId,
      ) {
        edges {
          node {
            id
            revisionId
            action
            metadata
            createdAt
            relatedResource {
              id
              pk
              type
              label
            }
          }
        }
        totalCount
      }
    }
    '''

    @classmethod
    def setUpTestData(cls):
        call_command('flush', interactive=False)

        super().setUpTestData()

        cls._run = Run.objects.get(
            pk='079d08c0-8c14-4c6f-90ee-ebc0b6c9b974'
        )

    @decorators.as_someone(['OWNER', 'MEMBER', 'READONLY'])
    def test_query(self):
        """Test the query.
        """
        table = Table.objects.filter(
            schema__datastore__id='x1nEp57xLm4N'
        ).first()

        node_id = helpers.to_global_id('TableType', table.pk)
        results = self.execute(self.statement, variables={'tableId': node_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=11,
            msg="Node count should equal number of revisions."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['OWNER'])
    def test_query_excludes_object_id_changes(self):
        """Test that the query exclude changes to the objectId field.
        """
        table = Table.objects.filter(
            schema__datastore__id='x1nEp57xLm4N'
        ).first()

        revision = Revision(
            revision_id=uuid.uuid4(),
            run=self._run,
            workspace_id=self._run.workspace_id,
            resource=table,
            parent_resource=table.schema,
            action=Revision.MODIFIED,
            metadata={'field': 'object_id', 'old_value': 1000, 'new_value': 2000},
        )
        revision.save()

        node_id = helpers.to_global_id('TableType', table.pk)
        results = self.execute(self.statement, variables={'tableId': node_id})
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=11,
            msg="Node count should equal number of revisions."
        )

        for edge in results['edges']:
            self.assertNotEqual(edge['node']['revisionId'], revision.revision_id)

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        table = Table.objects.filter(
            schema__datastore__id='x1nEp57xLm4N'
        ).first()

        node_id = helpers.to_global_id('TableType', table.pk)
        results = self.execute(self.statement, variables={'tableId': node_id})

        self.assertPermissionDenied(results)

    @decorators.as_someone(['ANONYMOUS'])
    def test_query_when_not_authenticated(self):
        """Outside users should not be able to access this resource.
        """
        table = Table.objects.filter(
            schema__datastore__id='x1nEp57xLm4N'
        ).first()

        node_id = helpers.to_global_id('TableType', table.pk)
        results = self.execute(self.statement, variables={'tableId': node_id})

        self.assertNotFound(results)


class TestGetRunHistoryWithError(cases.GraphQLTestCase):
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
            pk
            error {
              excMessage
            }
          }
        }
      }
    }
    '''

    def setUp(self):
        super(TestGetRunHistoryWithError, self).setUp()

        self.datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.global_id = helpers.to_global_id('DatastoreType', self.datastore.pk)
        self.run1 = self.factory(datastore=self.datastore)
        self.run2 = self.factory(datastore=self.datastore)
        self.error = self.run1.errors.create(
            task_id=None,
            task_fcn='test_function',
            exc_type='FakeExceptionClass',
            exc_message='This is an error message.',
            exc_stacktrace='This is a error message, but with the whole trace.'
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'datastoreId': self.global_id})
        results = results['data'][self.operation]

        run1 = next(filter(lambda r: r['node']['pk'] == str(self.run1.pk), results['edges']))
        run2 = next(filter(lambda r: r['node']['pk'] == str(self.run2.pk), results['edges']))

        self.assertEqual(run1['node']['error']['excMessage'], self.error.exc_message)
        self.assertEqual(run2['node']['error'], None)
