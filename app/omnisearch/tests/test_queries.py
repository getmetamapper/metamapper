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
    query GetSearchResults(
        $content: String!
        $datastores: [String]
    ) {
      omnisearch(content: $content, datastores: $datastores) {
        results {
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
        elapsed
      }
    }
    '''

    def setUp(self):
        super(TestOmnisearch, self).setUp()

        self.datastore = Datastore.objects.get(id='s4N8p5g0wjiS')
        self.other_datastore = factories.DatastoreFactory(workspace=self.workspace)
        self.other_schema = factories.SchemaFactory(datastore=self.other_datastore)
        self.other_table = factories.TableFactory(schema=self.other_schema, name='customers')

    def execute_search_query(self, content='customer information', datastores=None):
        """Used for consistent test results.
        """
        variables = {'content': content}
        if datastores:
            variables['datastores'] = datastores
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

        self.assertTrue(len(results['results']) == 0)
        self.assertTrue(isinstance(results['elapsed'], (float,)))

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    @mock.patch('app.omnisearch.queries.get_search_backend')
    def test_query_with_some_response(self, get_search_backend):
        """It should return whatever the search backend returns.
        """
        client = mock.MagicMock()
        client.to_dict.return_value = {
            'elapsed': 0.1,
            'results': [
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
            ],
            'facets': {},
        }

        get_search_backend.return_value = client

        results = self.execute_search_query()

        self.assertTrue(len(results['results']) == 2)
        self.assertTrue(isinstance(results['elapsed'], (float,)))

    @decorators.as_someone(['MEMBER', 'READONLY'])
    @mock.patch('app.omnisearch.queries.get_search_backend')
    def test_query_without_datastore_permission(self, get_search_backend):
        client = mock.MagicMock()
        client.user_permission_ids.return_value = ('woof', ['1', '2', '3'])

        get_search_backend.return_value = client

        results = self.execute_search_query(datastores=['4'])

        self.assertTrue(len(results['results']) == 0)
        self.assertTrue(isinstance(results['elapsed'], (float,)))

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_unauthorized(self):
        """It prevents unauthorized queries.
        """
        content = 'customer information'
        results = self.execute(self.statement, variables={'content': content})

        self.assertPermissionDenied(results)
