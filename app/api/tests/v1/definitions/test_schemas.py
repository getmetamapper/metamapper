# -*- coding: utf-8 -*-
from django.utils.crypto import get_random_string

from app.definitions.models import Datastore

import testutils.cases as cases
import testutils.factories as factories


class SchemaTestCase(cases.ApiTestCase):
    """Base class for Schema API test cases.
    """
    factory = factories.SchemaFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all Schema API test cases.
        """
        super().setUp()

        self.datastore = Datastore.objects.get(id='s4N8p5g0wjiS')
        self.schemas = self.factory.create_batch(
            self.factory_batch_size,
            datastore=self.datastore,
            workspace=self.workspace
        )

        self.schema = self.schemas[0]
        self.schema.name = 'public'
        self.schema.tags = ['alpha', 'beta', 'theta']
        self.schema.save()


class TestSchemaList(SchemaTestCase):
    def test_list(self):
        """It should list the results.
        """
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas')
        result = result.json()

        self.assertEqual(len(result['items']), self.factory_batch_size)
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.factory_batch_size,
            'results_per_page': 100,
        })

    def test_pagination(self):
        """It should paginate the results when a cursor is provided.
        """
        params = {'page_size': 5}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.factory_batch_size,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestSchemaDetail(SchemaTestCase):
    def test_get(self):
        """It should retrieve a single object.
        """
        result = self.client.get(f'/api/v1/schemas/{self.schema.object_id}')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.schema.object_id,
            'name': 'public',
            'tags': ['alpha', 'beta', 'theta'],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/schemas/{self.schema.object_id}')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/schemas/{self.schema.object_id}')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/schemas/{self.schema.object_id}')
        self.assertStatus(result, 405)

    def test_patch_valid(self):
        """It should update a single object.
        """
        params = {'tags': ['one', 'two']}
        result = self.client.patch(f'/api/v1/schemas/{self.schema.object_id}', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.schema.object_id,
            'name': 'public',
            'tags': ['one', 'two'],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_patch_invalid(self):
        """It should return an error response when invalid.
        """
        params = {'tags': [get_random_string(200)]}
        result = self.client.patch(f'/api/v1/schemas/{self.schema.object_id}', params)
        result_json = result.json()

        self.assertStatus(result, 400)
        self.assertEqual(result_json, {
            'success': False,
            'error': {
                'errors': [
                    {
                        'reason': 'max_length',
                        'message': 'Ensure this field has no more than 30 characters.',
                        'location_type': 'field',
                        'location': 'tags',
                    },
                ],
                'code': 400,
                'message': 'Input validation failed.',
            },
        })


class TestSchemaFind(SchemaTestCase):
    def test_exists(self):
        """It should retrieve a single object.
        """
        params = {'name': 'public'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas/find', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.schema.object_id,
            'name': 'public',
            'tags': ['alpha', 'beta', 'theta'],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_does_not_exist(self):
        """It should return a "404 - Not Found" error.
        """
        params = {'name': 'does_not_exist'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas/find', params)
        self.assertNotFound(result)

    def test_incorrect_parameters(self):
        """It should return a "400 - Invalid Request" error.
        """
        params = {'schema_name': 'public'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/schemas/find', params)
        self.assertParameterValidationFailed(result)

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/datastores/{self.datastore.id}/schemas/find')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/datastores/{self.datastore.id}/schemas/find')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/datastores/{self.datastore.id}/schemas/find')
        self.assertStatus(result, 405)
