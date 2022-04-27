# -*- coding: utf-8 -*-
from app.authorization.models import Group

import testutils.cases as cases
import testutils.factories as factories


class GroupTestCase(cases.ApiTestCase):
    """Base class for Group API test cases.
    """
    factory = factories.GroupFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all Group API test cases.
        """
        super().setUp()

        self.groups = self.factory.create_batch(
            self.factory_batch_size,
            workspace=self.workspace,
        )
        self.group = Group.objects.get(name="New York")
        for user in self.team_list:
            self.group.user_set.add(user)
        self.item_count = self.workspace.groups.count()


class TestGroupList(GroupTestCase):
    def test_list(self):
        """It should list the results.
        """
        result = self.client.get('/api/v1/groups')
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
        result = self.client.get('/api/v1/groups', params)
        result = result.json()

        self.assertEqual(len(result['items']), params['page_size'])
        self.assertIsNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': self.item_count,
            'results_per_page': params['page_size'],
        })

        params = {'page_size': 5, 'cursor': result['next_page_token']}
        result = self.client.get('/api/v1/groups', params)
        result = result.json()

        self.assertIsNotNone(result['prev_page_token'])
        self.assertIsNotNone(result['next_page_token'])


class TestGroupFind(GroupTestCase):
    def test_exists(self):
        """It should retrieve a single object.
        """
        params = {'name': 'New York'}
        result = self.client.get('/api/v1/groups/find', params)
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.group.id,
            'name': 'New York',
            'description': 'Employees from New York',
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_does_not_exist(self):
        """It should return a "404 - Not Found" error.
        """
        params = {'name': 'does_not_exist'}
        result = self.client.get('/api/v1/groups/find', params)
        self.assertNotFound(result)

    def test_incorrect_parameters(self):
        """It should return a "400 - Invalid Request" error.
        """
        params = {'other': 'public'}
        result = self.client.get('/api/v1/groups/find', params)
        self.assertParameterValidationFailed(result)

    def test_post(self):
        """It should not be able to make a POST request.
        """
        params = {'name': 'public'}
        result = self.client.post('/api/v1/groups/find', params)
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        params = {'name': 'public'}
        result = self.client.put('/api/v1/groups/find', params)
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        params = {'name': 'public'}
        result = self.client.delete('/api/v1/groups/find', params)
        self.assertStatus(result, 405)


class TestGroupUserList(GroupTestCase):
    def test_list(self):
        """It should list the results.
        """
        params = {'page_size': 3}
        result = self.client.get(f'/api/v1/groups/{self.group.id}/users', params)
        result = result.json()

        self.assertIsNone(result['prev_page_token'])
        self.assertIsNone(result['next_page_token'])
        self.assertEqual(result['page_info'], {
            'total_results': len(self.team_list),
            'results_per_page': params['page_size'],
        })

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/groups/{self.group.id}/users')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/groups/{self.group.id}/users')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/groups/{self.group.id}/users')
        self.assertStatus(result, 405)
