# -*- coding: utf-8 -*-
import unittest.mock as mock

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

    def execute_search_query(self, content='customer information', datastore_id=None):
        """Used for consistent test results.
        """
        variables = {'content': content}
        if datastore_id:
            variables['datastoreId'] = datastore_id
        results = self.execute(self.statement, variables=variables)
        results = results['data'][self.operation]
        return results

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    @mock.patch('app.omnisearch.queries.get_search_backend')
    def test_query_with_no_response(self, get_search_backend):
        """It should return an empty list.
        """
        client = mock.MagicMock()
        client.search.return_value = []

        get_search_backend.return_value = client

        results = self.execute_search_query()

        self.assertTrue(len(results['searchResults']) == 0)
        self.assertTrue(isinstance(results['timeElapsed'], (float,)))

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    @mock.patch('app.omnisearch.queries.get_search_backend')
    def test_query_with_some_response(self, get_search_backend):
        """It should return whatever the search backend returns.
        """
        client = mock.MagicMock()
        client.search.return_value = [
            {
                'pk': 1,
                'model_name': 'Column',
                'score': 0.10,
                'datastore_id': 'meow',
            },
            {
                'pk': 2,
                'model_name': 'Table',
                'score': 0.75,
                'datastore_id': 'meow',
            }
        ]

        get_search_backend.return_value = client

        results = self.execute_search_query()

        self.assertTrue(len(results['searchResults']) == 2)
        self.assertTrue(isinstance(results['timeElapsed'], (float,)))

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    @mock.patch('app.omnisearch.queries.get_search_backend')
    def test_query_without_datastore_permission(self, get_search_backend):
        """It should return results for all datastores in the workspace.
        """
        client = mock.MagicMock()
        client.user_permission_ids.return_value = ('woof', ['1', '2', '3'])

        get_search_backend.return_value = client

        results = self.execute_search_query(datastore_id='4')

        self.assertTrue(len(results['searchResults']) == 0)
        self.assertTrue(isinstance(results['timeElapsed'], (float,)))

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_unauthorized(self):
        """It prevents unauthorized queries.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})

        self.assertPermissionDenied(results)
