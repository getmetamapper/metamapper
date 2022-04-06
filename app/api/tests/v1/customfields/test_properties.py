# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

import testutils.cases as cases
import testutils.factories as factories


class CustomFieldTestCase(cases.ApiTestCase):
    """Base class for Custom Field API test cases.
    """
    factory = factories.CustomFieldFactory
    factory_batch_size = 15

    def setUp(self):
        """Initial setup for all Custom Field API test cases.
        """
        super().setUp()

        self.custom_fields = self.factory.create_batch(
            self.factory_batch_size,
            workspace=self.workspace
        )

        self.content_types = {
            c.id: c for c in ContentType.objects.all()
        }

        self.related_types = {
            'datastore': 0,
            'table': 0,
        }

        self.custom_field = self.custom_fields[0]
        self.custom_field.content_type = ContentType.objects.get(model='datastore')
        self.custom_field.field_name = 'ETL Frequency'
        self.custom_field.field_type = 'ENUM'
        self.custom_field.validators = {'choices': ['Daily', 'Weekly', 'Monthly']}
        self.custom_field.short_desc = 'Out yes road.'
        self.custom_field.save()

        for field in self.custom_fields:
            self.related_types[self.content_types[field.content_type_id].model] += 1


class TestCustomFieldList(CustomFieldTestCase):
    def test_list(self):
        """It should list the results.
        """
        for related_type, related_type_count in self.related_types.items():
            params = {'page_size': 5, 'related_type': related_type}
            result = self.client.get('/api/v1/properties', params)
            result = result.json()

            self.assertEqual(len(result['items']), min(params['page_size'], related_type_count))
            self.assertEqual(result['page_info'], {
                'total_results': related_type_count,
                'results_per_page': params['page_size'],
            })

    def test_list_without_type(self):
        """It should return a 400 error response.
        """
        params = {'page_size': 5}
        result = self.client.get('/api/v1/properties', params)
        self.assertParameterValidationFailed(result)

    def test_list_with_invalid_type(self):
        """It should return a 400 error response.
        """
        params = {'page_size': 5, 'related_type': 'assets'}
        result = self.client.get('/api/v1/properties', params)
        self.assertParameterValidationFailed(result)


class TestCustomFieldDetail(CustomFieldTestCase):
    def test_get(self):
        """It should retrieve a single object.
        """
        result = self.client.get(f'/api/v1/properties/{self.custom_field.id}')
        result_json = result.json()

        self.assertOk(result)
        self.assertEqual(result_json, {
            'id': self.custom_field.id,
            'related_type': 'datastore',
            'field_name': 'ETL Frequency',
            'field_type': 'ENUM',
            'short_desc': 'Out yes road.',
            'validators': {'choices': ['Daily', 'Weekly', 'Monthly']},
            'created_at': result_json['created_at'],
            'updated_at': result_json['updated_at'],
        })

    def test_post(self):
        """It should not be able to make a POST request.
        """
        result = self.client.post(f'/api/v1/properties/{self.custom_field.id}')
        self.assertStatus(result, 405)

    def test_put(self):
        """It should not be able to make a PUT request.
        """
        result = self.client.put(f'/api/v1/properties/{self.custom_field.id}')
        self.assertStatus(result, 405)

    def test_delete(self):
        """It should not be able to make a DELETE request.
        """
        result = self.client.delete(f'/api/v1/properties/{self.custom_field.id}')
        self.assertStatus(result, 405)

    def test_patch(self):
        """It should not be able to make a PATCH request.
        """
        result = self.client.patch(f'/api/v1/properties/{self.custom_field.id}')
        self.assertStatus(result, 405)
