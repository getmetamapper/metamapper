# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories

from app.definitions.models import Datastore


class TestOmnisearch(cases.GraphQLTestCase):
    """Test cases for listing all datastores in a workspace.
    """
    load_data = [
        'workspaces.json',
        'users.json',
        'datastore.json',
        'comments.json',
    ]

    operation = 'omnisearch'
    statement = '''
    query getSearchResults($content: String!, $datastoreId: String) {
      omnisearch(content: $content, datastoreId: $datastoreId) {
        searchResults {
          pk
          modelName
          score
          datastoreId
          searchResult {
            label
            description
            pathname
          }
        }
        timeElapsed
      }
    }
    '''

    def setUp(self):
        super(TestOmnisearch, self).setUp()

        self.datastore = Datastore.objects.get(id='s4N8p5g0wjiS')
        self.other_datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.other_schema = factories.SchemaFactory(datastore=self.other_datastore)
        self.other_table = factories.TableFactory(schema=self.other_schema, name='customers')

    def execute_search_query(self):
        """Used for consistent test results.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})
        results = results['data'][self.operation]
        return results

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_object_permissions_are_disabled(self):
        """It should return results for all datastores in the workspace.
        """
        results = self.execute_search_query()

        self.assertTrue(len(results) > 1)
        self.assertTrue(isinstance(results['timeElapsed'], (float,)))
        self.assertTrue(str(self.other_table.pk) in [d['pk'] for d in results['searchResults']])
        self.assertEqual(set([d['modelName'] for d in results['searchResults']]), {'Column', 'Comment', 'Table'})
        self.assertEqual(
            set([d['datastoreId'] for d in results['searchResults']]),
            {self.datastore.id, self.other_datastore.id},
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_when_object_permissions_are_enabled_without_access(self):
        """It filter out datastore results if does not have permissions.
        """
        self.other_datastore.object_permissions_enabled = True
        self.other_datastore.save()

        results = self.execute_search_query()

        self.assertTrue(len(results) > 1)
        self.assertEqual(
            set([d['datastoreId'] for d in results['searchResults']]),
            {self.datastore.id},
        )

    @decorators.as_someone(['MEMBER', 'READONLY'])
    def test_query_when_object_permissions_are_enabled_with_access(self):
        """It should honor object-level permissions when enabled.
        """
        self.other_datastore.object_permissions_enabled = True
        self.other_datastore.save()
        self.other_datastore.assign_perm(self.user, 'definitions.view_datastore')

        results = self.execute_search_query()

        self.assertTrue(len(results) > 1)
        self.assertEqual(
            set([d['datastoreId'] for d in results['searchResults']]),
            {self.datastore.id, self.other_datastore.id},
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_returns_results_for_a_single_datastore(self):
        """It should allow you to scope your query to a specific datastore.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={
            'content': content,
            'datastoreId': self.other_datastore.pk,
        })
        results = results['data'][self.operation]

        self.assertTrue(len(results['searchResults']) == 1)
        self.assertEqual(
            set([d['datastoreId'] for d in results['searchResults']]),
            {self.other_datastore.id},
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_returns_results_for_only_this_workspace(self):
        """It should not return results from other datastores.
        """
        table = factories.TableFactory(name='customers')

        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})
        results = results['data'][self.operation]

        self.assertTrue(table.pk not in [d['pk'] for d in results['searchResults']])

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_unauthorized(self):
        """It prevents unauthorized queries.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})

        self.assertPermissionDenied(results)
