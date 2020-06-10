# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories


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

        self.other_datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.other_schema = factories.SchemaFactory(datastore=self.other_datastore)
        self.other_table = factories.TableFactory(schema=self.other_schema, name='customers')

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_returns_results_for_all_datastores(self):
        """It should return results for all datastores in the workspace.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})
        results = results['data'][self.operation]

        self.assertTrue(len(results) > 1)
        self.assertTrue(isinstance(results['timeElapsed'], (float,)))
        self.assertTrue(self.other_table.pk in [d['pk'] for d in results['searchResults']])
        self.assertEqual(set([d['modelName'] for d in results['searchResults']]), {'Column', 'Comment', 'Table'})

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_returns_results_for_a_single_datastores(self):
        """It should allow you to scope your query to a specific datastore.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={
            'content': content,
            'datastoreId': self.other_datastore.pk,
        })
        results = results['data'][self.operation]

        self.assertTrue(len(results['searchResults']) == 1)

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
