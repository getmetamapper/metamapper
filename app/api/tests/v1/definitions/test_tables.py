# -*- coding: utf-8 -*-
from django.utils.crypto import get_random_string

from app.definitions.models import AssetOwner, Datastore

from app.authorization.models import Group

import testutils.cases as cases
import testutils.factories as factories


class TableTestCase(cases.ApiTestCase):
    """Base class for Table API test cases.
    """
    load_data = ['workspaces.json', 'users.json', 'customfields.json']

    factory = factories.TableFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all Table API test cases.
        """
        super().setUp()

        self.datastore = Datastore.objects.get(id='s4N8p5g0wjiS')

        self.schema = factories.SchemaFactory(datastore=self.datastore, name='app')
        self.tables = self.factory.create_batch(
            self.factory_batch_size,
            schema=self.schema,
            workspace=self.workspace
        )
        self.outside_tables = self.factory.create_batch(
            5,
            schema=factories.SchemaFactory(datastore=self.datastore),
            workspace=self.workspace
        )
        self.total_table_count = len(self.tables) + len(self.outside_tables)
        self.table = self.tables[0]
        self.table.name = 'users'
        self.table.tags = ['alpha', 'beta', 'theta']
        self.table.custom_properties = {
            'YjOTcEUsymIU': self.users['OWNER'].pk,
            'p0tqRz5QJ9yC': 'Finance',
            'zI5j91vH0cfI': 'Hourly',
            'does_not_exist': 'Should not be there',
        }
        self.table.save()

        default_owner_kwargs = {
            "content_object": self.table,
            "workspace": self.workspace,
        }
        group = Group.objects.get(id=12412)

        AssetOwner.objects.create(owner=self.users['MEMBER'], **default_owner_kwargs)
        AssetOwner.objects.create(owner=group, **default_owner_kwargs)


class TestDatastoreTableList(TableTestCase):
    def test_list(self):
        """It should list the results for all tables in the datastore.
        """
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables')
        result = result.json()

        self.assertEqual(len(result['items']), self.total_table_count)
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.total_table_count,
            'results_per_page': 100,
        })

    def test_pagination(self):
        """It should paginate the results when a cursor is provided.
        """
        params = {'page_size': 5}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.total_table_count,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestTableList(TableTestCase):
    def test_list(self):
        """It should list the results.
        """
        result = self.client.get(f'/api/v1/schemas/{self.schema.object_id}/tables')
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
        result = self.client.get(f'/api/v1/schemas/{self.schema.object_id}/tables', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.factory_batch_size,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get(f'/api/v1/schemas/{self.schema.object_id}/tables', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestTableDetail(TableTestCase):
    def test_get(self):
        """It should retrieve a single object.
        """
        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.table.object_id,
            'name': 'users',
            'kind': 'TABLE',
            'short_desc': None,
            'tags': ['alpha', 'beta', 'theta'],
            'readme': None,
            'owners': [
                {
                    'id': 4,
                    'name': 'David Wallace',
                    'type': 'USER',
                },
                {
                    'id': 12412,
                    'name': 'New York',
                    'type': 'GROUP',
                },
            ],
            'properties': [
                {
                    'id': 'YjOTcEUsymIU',
                    'label': 'Data Steward',
                    'value': {
                        'id': 1,
                        'name': 'Sam Crust',
                        'type': 'USER',
                    },
                },
                {
                    'id': 'p0tqRz5QJ9yC',
                    'label': 'Product Area',
                    'value': 'Finance',
                },
                {
                    'id': 'zI5j91vH0cfI',
                    'label': 'Update Cadence',
                    'value': 'Hourly',
                },
            ],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/tables/{self.table.object_id}')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/tables/{self.table.object_id}')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}')
        self.assertStatus(result, 405)

    def test_patch_valid(self):
        """It should update a single object.
        """
        params = {'short_desc': 'This is a short description.', 'readme': '<script>alert(\'test\');</script>'}
        result = self.client.patch(f'/api/v1/tables/{self.table.object_id}', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.table.object_id,
            'name': 'users',
            'kind': 'TABLE',
            'short_desc': 'This is a short description.',
            'tags': ['alpha', 'beta', 'theta'],
            'readme': '&lt;script&gt;alert(\'test\');&lt;/script&gt;',
            'owners': [
                {
                    'id': 4,
                    'name': 'David Wallace',
                    'type': 'USER',
                },
                {
                    'id': 12412,
                    'name': 'New York',
                    'type': 'GROUP',
                },
            ],
            'properties': [
                {
                    'id': 'YjOTcEUsymIU',
                    'label': 'Data Steward',
                    'value': {
                        'id': 1,
                        'name': 'Sam Crust',
                        'type': 'USER',
                    },
                },
                {
                    'id': 'p0tqRz5QJ9yC',
                    'label': 'Product Area',
                    'value': 'Finance',
                },
                {
                    'id': 'zI5j91vH0cfI',
                    'label': 'Update Cadence',
                    'value': 'Hourly',
                },
            ],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_patch_invalid(self):
        """It should return an error response when invalid.
        """
        params = {'short_desc': get_random_string(200), 'tags': [str(i) for i in range(20)]}
        result = self.client.patch(f'/api/v1/tables/{self.table.object_id}', params)
        result_json = result.json()

        self.assertStatus(result, 400)
        self.assertEqual(result_json, {
            'success': False,
            'error': {
                'errors': [
                    {
                        'reason': 'max_length',
                        'message': 'Ensure this field has no more than 140 characters.',
                        'location_type': 'field',
                        'location': 'short_desc',
                    },
                    {
                        'reason': 'max_length',
                        'message': 'Ensure this field has no more than 10 elements.',
                        'location_type': 'field',
                        'location': 'tags',
                    },
                ],
                'code': 400,
                'message': 'Input validation failed.',
            },
        })


class TestTableFind(TableTestCase):
    def test_exists(self):
        """It should retrieve a single object.
        """
        params = {'schema': 'app', 'name': 'users'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables/find', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.table.object_id,
            'name': 'users',
            'kind': 'TABLE',
            'short_desc': None,
            'tags': ['alpha', 'beta', 'theta'],
            'readme': None,
            'owners': [
                {
                    'id': 4,
                    'name': 'David Wallace',
                    'type': 'USER',
                },
                {
                    'id': 12412,
                    'name': 'New York',
                    'type': 'GROUP',
                },
            ],
            'properties': [
                {
                    'id': 'YjOTcEUsymIU',
                    'label': 'Data Steward',
                    'value': {
                        'id': 1,
                        'name': 'Sam Crust',
                        'type': 'USER',
                    },
                },
                {
                    'id': 'p0tqRz5QJ9yC',
                    'label': 'Product Area',
                    'value': 'Finance',
                },
                {
                    'id': 'zI5j91vH0cfI',
                    'label': 'Update Cadence',
                    'value': 'Hourly',
                },
            ],
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_does_not_exist(self):
        """It should return a "404 - Not Found" error.
        """
        params = {'schema': 'app', 'name': 'does_not_exist'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables/find', params)
        self.assertNotFound(result)

    def test_incorrect_parameters(self):
        """It should return a "400 - Invalid Request" error.
        """
        params = {'schema': 'app'}
        result = self.client.get(f'/api/v1/datastores/{self.datastore.id}/tables/find', params)
        self.assertParameterValidationFailed(result)

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/datastores/{self.datastore.id}/tables/find')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/datastores/{self.datastore.id}/tables/find')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/datastores/{self.datastore.id}/tables/find')
        self.assertStatus(result, 405)


class TestTableProperties(TableTestCase):
    def test_patch_valid(self):
        """It should update the table properties.
        """
        params = {'properties': [{'id': 'zI5j91vH0cfI', 'value': 'Daily'}, {'id': 'YjOTcEUsymIU', 'value': 3}]}
        result = self.client.patch(f'/api/v1/tables/{self.table.object_id}/properties', params, format='json')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {'success': True})

        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertEqual(result_json['properties'], [
            {'id': 'YjOTcEUsymIU', 'label': 'Data Steward', 'value': {'id': 3, 'name': 'Dwight Schrute', 'type': 'USER'}},
            {'id': 'p0tqRz5QJ9yC', 'label': 'Product Area', 'value': 'Finance'},
            {'id': 'zI5j91vH0cfI', 'label': 'Update Cadence', 'value': 'Daily'},
        ])

    def test_patch_removal(self):
        """It should update the table properties.
        """
        params = {'properties': [{'id': 'zI5j91vH0cfI', 'value': None}, {'id': 'YjOTcEUsymIU', 'value': None}]}
        result = self.client.patch(f'/api/v1/tables/{self.table.object_id}/properties', params, format='json')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {'success': True})

        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertEqual(result_json['properties'], [
            {'id': 'p0tqRz5QJ9yC', 'label': 'Product Area', 'value': 'Finance'},
        ])

    def test_patch_invalid(self):
        """It should throw a 400 error.
        """
        params = {'properties': [{'id': 'meowmeowmeow', 'value': 'Marketing'}]}
        result = self.client.patch(f'/api/v1/tables/{self.table.object_id}/properties', params, format='json')
        result_json = result.json()

        self.assertStatus(result, 400)
        self.assertEqual(result_json, {
            'success': False,
            'error': {
                'errors': [
                    {
                        'reason': 'invalid',
                        'message': 'This custom property does not exist.',
                        'location_type': 'property',
                        'location': 'meowmeowmeow',
                    },
                ],
                'code': 400,
                'message': 'Input validation failed.',
            },
        })

    def test_delete_valid(self):
        """It should remove the provided table properties.
        """
        params = {'properties': ['zI5j91vH0cfI']}
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}/properties', params, format='json')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {'success': True})

        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertEqual(result_json['properties'], [
            {'id': 'YjOTcEUsymIU', 'label': 'Data Steward', 'value': {'id': 1, 'name': 'Sam Crust', 'type': 'USER'}},
            {'id': 'p0tqRz5QJ9yC', 'label': 'Product Area', 'value': 'Finance'},
        ])

    def test_delete_invalid(self):
        """It should throw a 400 error.
        """
        params = {'properties': ['meowmeowmeow']}
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}/properties', params, format='json')
        result_json = result.json()

        self.assertStatus(result, 400)
        self.assertEqual(result_json, {
            'success': False,
            'error': {
                'errors': [
                    {
                        'reason': 'invalid',
                        'message': 'This custom property does not exist.',
                        'location_type': 'property',
                        'location': 'meowmeowmeow',
                    },
                ],
                'code': 400,
                'message': 'Input validation failed.',
            },
        })


class TestTableOwner(TableTestCase):
    def test_post_valid(self):
        """It should add the table owner.
        """
        params = {'owner_id': 3, 'owner_type': 'USER'}
        result = self.client.post(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {'success': True})

        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json['owners'], [
            {'id': 4, 'name': 'David Wallace', 'type': 'USER'},
            {'id': 3, 'name': 'Dwight Schrute', 'type': 'USER'},
            {'id': 12412, 'name': 'New York', 'type': 'GROUP'},
        ])

    def test_post_invalid_instance(self):
        """It should throw a validation error.
        """
        params = {'owner_id': 45000, 'owner_type': 'USER'}
        result = self.client.post(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        self.assertNotFound(result)

    def test_post_invalid_parameter(self):
        """It should throw a validation error.
        """
        params = {'owner_id': 45000}
        result = self.client.post(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        self.assertParameterValidationFailed(result)

    def test_delete_valid(self):
        """It should remove the table owner.
        """
        params = {'owner_id': 4, 'owner_type': 'USER'}
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {'success': True})

        result = self.client.get(f'/api/v1/tables/{self.table.object_id}')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json['owners'], [
            {'id': 12412, 'name': 'New York', 'type': 'GROUP'},
        ])

    def test_delete_invalid_instance(self):
        """It should throw a validation error.
        """
        params = {'owner_id': 45000, 'owner_type': 'USER'}
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        self.assertNotFound(result)

    def test_delete_invalid_parameter(self):
        """It should throw a validation error.
        """
        params = {'owner_id': 45000}
        result = self.client.delete(f'/api/v1/tables/{self.table.object_id}/owners', params, format='json')
        self.assertParameterValidationFailed(result)
