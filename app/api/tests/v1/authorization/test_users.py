# -*- coding: utf-8 -*-
from app.authorization.models import Membership

import testutils.cases as cases
import testutils.factories as factories


class UserTestCase(cases.ApiTestCase):
    """Base class for User API test cases.
    """
    factory = factories.UserFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all User API test cases.
        """
        super().setUp()

        self.users = self.factory.create_batch(self.factory_batch_size)

        for user in self.users:
            self.workspace.grant_membership(user, Membership.MEMBER)

        self.item_count = self.workspace.memberships.count()


class TestUserList(UserTestCase):
    def test_list(self):
        """It should list the results.
        """
        result = self.client.get('/api/v1/users')
        result = result.json()

        self.assertEqual(len(result['items']), self.item_count)
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.item_count,
            'results_per_page': 100,
        })

    def test_pagination(self):
        """It should paginate the results when a cursor is provided.
        """
        params = {'page_size': 5}
        result = self.client.get('/api/v1/users', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.item_count,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get('/api/v1/users', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestUserFind(UserTestCase):
    def test_exists(self):
        """It should retrieve a single object.
        """
        params = {'email': 'member@metamapper.io'}
        result = self.client.get('/api/v1/users/find', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': 4,
            'name': 'David Wallace',
            'email': 'member@metamapper.io',
            'permissions': 'MEMBER',
            'created_at': result_json['created_at'],
        })

    def test_does_not_exist(self):
        """It should return a "404 - Not Found" error.
        """
        params = {'email': 'does_not_exist'}
        result = self.client.get('/api/v1/users/find', params)
        self.assertNotFound(result)

    def test_incorrect_parameters(self):
        """It should return a "400 - Invalid Request" error.
        """
        params = {'name': 'public'}
        result = self.client.get('/api/v1/users/find', params)
        self.assertParameterValidationFailed(result)

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post('/api/v1/users/find')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put('/api/v1/users/find')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete('/api/v1/users/find')
        self.assertStatus(result, 405)
