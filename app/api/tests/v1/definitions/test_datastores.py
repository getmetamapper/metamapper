# -*- coding: utf-8 -*-
from django.utils.crypto import get_random_string

import testutils.cases as cases
import testutils.factories as factories


class DatastoreTestCase(cases.ApiTestCase):
    """Base class for Datastore API test cases.
    """
    load_data = ['workspaces.json', 'users.json', 'customfields.json']

    factory = factories.DatastoreFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all Datastore API test cases.
        """
        super().setUp()

        self.datastores = self.factory.create_batch(
            self.factory_batch_size,
            workspace=self.workspace
        )

        # We seed one datastore as part of the workspaces.json
        # fixture, so we add that to the total count.
        self.datastore_count = self.factory_batch_size + 1


class TestDatastoreList(DatastoreTestCase):
    def test_list(self):
        """It should list the results.
        """
        result = self.client.get('/api/v1/datastores')
        result = result.json()

        self.assertEqual(len(result['items']), self.datastore_count)
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.datastore_count,
            'results_per_page': 100,
        })

    def test_pagination(self):
        """It should paginate the results when a cursor is provided.
        """
        params = {'page_size': 5}
        result = self.client.get('/api/v1/datastores', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.datastore_count,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get('/api/v1/datastores', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestDatastoreDetail(DatastoreTestCase):
    def test_get(self):
        """It should retrieve a single datastore object.
        """
        result = self.client.get('/api/v1/datastores/s4N8p5g0wjiS')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': 's4N8p5g0wjiS',
            'name': 'Postgres',
            'slug': 'metamapper',
            'engine': 'postgresql',
            'version': '9.6.1',
            'is_enabled': True,
            'short_desc': None,
            'tags': [],
            'properties': [
                {
                    'id': 'ow5W0kw0CK0i',
                    'label': 'Ownership',
                    'value': 'Analytics',
                },
                {
                    'id': 'iPOhV1HazLW6',
                    'label': 'Purpose',
                    'value': 'Business Intelligence',
                },
            ],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post('/api/v1/datastores/s4N8p5g0wjiS')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put('/api/v1/datastores/s4N8p5g0wjiS')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete('/api/v1/datastores/s4N8p5g0wjiS')
        self.assertStatus(result, 405)

    def test_patch_valid(self):
        """It should update a single datastore object.
        """
        params = {'tags': ['one', 'two'], 'short_desc': 'This is a test.'}
        result = self.client.patch('/api/v1/datastores/s4N8p5g0wjiS', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': 's4N8p5g0wjiS',
            'name': 'Postgres',
            'slug': 'metamapper',
            'engine': 'postgresql',
            'version': '9.6.1',
            'is_enabled': True,
            'short_desc': params['short_desc'],
            'tags': params['tags'],
            'properties': [
                {
                    'id': 'ow5W0kw0CK0i',
                    'label': 'Ownership',
                    'value': 'Analytics',
                },
                {
                    'id': 'iPOhV1HazLW6',
                    'label': 'Purpose',
                    'value': 'Business Intelligence',
                },
            ],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_patch_invalid(self):
        """It should return an error response when invalid.
        """
        params = {'short_desc': get_random_string(200)}
        result = self.client.patch('/api/v1/datastores/s4N8p5g0wjiS', params)
        result_json = result.json()

        self.assertStatus(result, 400)
        self.assertEqual(result_json, {
            'short_desc': [
                'Ensure this field has no more than 140 characters.',
            ],
        })


class TestDatastoreProperties(DatastoreTestCase):
    pass
