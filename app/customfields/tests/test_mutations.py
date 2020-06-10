# -*- coding: utf-8 -*-
import app.customfields.models as models

import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers


class CreateCustomFieldTests(cases.GraphQLTestCase):
    """Tests for creating a custom field.
    """
    factory = factories.CustomFieldFactory

    operation = 'createCustomField'
    statement = '''
    mutation CreateCustomField(
      $fieldName: String!,
      $fieldType: String!,
      $validators: JSONObject!,
      $contentType: String!,
    ) {
      createCustomField(input: {
        fieldName: $fieldName,
        fieldType: $fieldType,
        validators: $validators,
        contentType: $contentType,
      }) {
        customField {
          pk
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'fieldName': helpers.faker.name(),
            'fieldType': models.CustomField.ENUM,
            'validators': {
                'choices': [
                    'one',
                    'two',
                    'three',
                ],
            },
        }
        attributes.update(**overrides)
        return attributes

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_datastore(self):
        """It should create a CustomField scoped to Datastore models.
        """
        variables = self._get_attributes(contentType='datastore')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertInstanceCreated(
            model_class=models.CustomField,
            field_name=variables['fieldName'],
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_table(self):
        """It should create a CustomField scoped to Table models.
        """
        variables = self._get_attributes(contentType='table')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertInstanceCreated(
            model_class=models.CustomField,
            field_name=variables['fieldName'],
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid_content_type(self):
        """It should throw a validation error when a validators are invalid.
        """
        variables = self._get_attributes(contentType='random')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': None,
            'errors': [
                {
                    'resource': 'CustomField',
                    'field': 'content_type',
                    'code': 'nulled',
                }
            ],
        })

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid_type(self):
        """It should throw a validation error when a fieldType is not supported.
        """
        variables = self._get_attributes(contentType='table', fieldType='INTEGER')

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': None,
            'errors': [
                {
                    'resource': 'CustomField',
                    'field': 'field_type',
                    'code': 'invalid_choice',
                }
            ],
        })

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid_validators(self):
        """It should throw a validation error when a validators are invalid.
        """
        variables = self._get_attributes(
            contentType='table',
            fieldType=models.CustomField.ENUM,
            validators={},
        )

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': None,
            'errors': [
                {
                    'resource': 'CustomField',
                    'field': 'choices',
                    'code': 'required',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        variables = self._get_attributes(contentType='table')
        self.assertPermissionDenied(self.execute(variables=variables))


class UpdateCustomFieldTests(cases.GraphQLTestCase):
    """Tests for updating a custom field.
    """
    factory = factories.CustomFieldFactory

    operation = 'updateCustomField'
    statement = '''
    mutation UpdateCustomField(
      $id: ID!,
      $fieldName: String,
      $validators: JSONObject,
    ) {
      updateCustomField(input: {
        id: $id,
        fieldName: $fieldName,
        validators: $validators,
      }) {
        customField {
          fieldName
          fieldType
          validators
        }
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_datastore(self):
        """It should create a CustomField scoped to Table models.
        """
        resource = self.factory(workspace=self.workspace, field_type=models.CustomField.TEXT)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        variables = {
            'id': globalid,
            'fieldName': helpers.faker.name(),
            'validators': {},
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': {
                'fieldName': variables['fieldName'],
                'fieldType': models.CustomField.TEXT,
                'validators': variables['validators'],
            },
            'errors': None
        })

        self.assertInstanceUpdated(
            instance=resource,
            field_name=variables['fieldName'],
            validators=variables['validators'],
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_table(self):
        """It should create a CustomField scoped to Table models.
        """
        resource = self.factory(workspace=self.workspace, field_type=models.CustomField.ENUM)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        variables = {
            'id': globalid,
            'fieldName': helpers.faker.name(),
            'validators': {
                'choices': ['red', 'blue', 'yellow']
            }
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': {
                'fieldName': variables['fieldName'],
                'fieldType': models.CustomField.ENUM,
                'validators': variables['validators'],
            },
            'errors': None
        })

        self.assertInstanceUpdated(
            instance=resource,
            field_name=variables['fieldName'],
            validators=variables['validators'],
        )

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_invalid_validators(self):
        """It should throw a validation error when a validators are invalid.
        """
        resource = self.factory(workspace=self.workspace, field_type=models.CustomField.ENUM)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        variables = {
            'id': globalid,
            'validators': {
                'choices': None,
            },
        }

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customField': None,
            'errors': [
                {
                    'resource': 'CustomField',
                    'field': 'choices',
                    'code': 'nulled',
                }
            ],
        })

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        variables = {
            'id': globalid,
            'fieldName': 'New Name',
        }

        self.assertPermissionDenied(self.execute(variables=variables))


class DeleteCustomFieldTests(cases.GraphQLTestCase):
    """Tests for deleting a custom field.
    """
    factory = factories.CustomFieldFactory

    operation = 'deleteCustomField'
    statement = '''
    mutation DeleteCustomField(
      $id: ID!,
    ) {
      deleteCustomField(input: {
        id: $id,
      }) {
        ok
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid(self):
        """It should permanently delete the custom field.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        response = self.execute(variables={'id': globalid})
        response = response['data'][self.operation]

        self.assertOk(response)
        self.assertInstanceDeleted(
            model_class=models.CustomField,
            pk=resource.pk,
            workspace_id=self.workspace.id,
        )

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_unauthorized(self):
        """It should return a "Permission Denied" error.
        """
        resource = self.factory(workspace=self.workspace)
        globalid = helpers.to_global_id('CustomFieldType', resource.pk)

        response = self.execute(variables={'id': globalid})

        self.assertPermissionDenied(response)

    def test_does_not_exist(self):
        """It should return a "Resource Not Found" error.
        """
        globalid = helpers.to_global_id('CustomFieldType', '12345')
        response = self.execute(variables={'id': globalid})

        self.assertNotFound(response)


class UpdateCustomPropertiesTests(cases.GraphQLTestCase):
    """Tests for updating custom properties.
    """
    factory = factories.CustomFieldFactory

    operation = 'updateCustomProperties'
    statement = '''
    mutation UpdateCustomProperties(
      $objectId: ID!,
      $properties: [JSONObject]!,
    ) {
      updateCustomProperties(input: {
        objectId: $objectId,
        properties: $properties,
      }) {
        customProperties
        errors {
          resource
          field
          code
        }
      }
    }
    '''

    def _test_valid_for_content_type(self, resource, globalid):
        """Helper function for testing different content types.
        """
        attributes = {
            'content_type': resource.content_type,
            'workspace': self.workspace,
        }

        customfields = [
            factories.CustomFieldFactory(
                field_name='Steward',
                field_type=models.CustomField.USER,
                validators={},
                **attributes,
            ),
            factories.CustomFieldFactory(
                field_name='Product Area',
                field_type=models.CustomField.TEXT,
                validators={},
                **attributes,
            ),
            factories.CustomFieldFactory(
                field_name='Team',
                field_type=models.CustomField.ENUM,
                validators={'choices': ['Data Engineering', 'Product', 'Design']},
                **attributes,
            ),
        ]

        variables = {
            'objectId': globalid,
            'properties': [
                {
                    'id': customfields[0].pk,
                    'value': self.user.pk,
                },
                {
                    'id': customfields[1].pk,
                    'value': helpers.faker.name(),
                },
                {
                    'id': customfields[2].pk,
                    'value': 'Product',
                }
            ]
        }

        current_user = {
            'pk': self.user.pk,
            'name': self.user.name,
            'email': self.user.email,
            'type': 'User',
        }

        expected = []

        for f in customfields:
            v = next(filter(lambda p: p['id'] == f.pk, variables['properties']), {})
            expected.append({
                'fieldId': f.pk,
                'fieldLabel': f.field_name,
                'fieldValue': v.get('value') if f.field_name != 'Steward' else current_user
            })

        response = self.execute(variables=variables)
        response = response['data'][self.operation]

        self.assertEqual(response, {
            'customProperties': expected,
            'errors': None,
        })

        for c in customfields:
            c.delete()

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_datastore(self):
        """It should update the custom properties.
        """
        resource = factories.DatastoreFactory(workspace=self.workspace)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        self._test_valid_for_content_type(resource, globalid)

    @decorators.as_someone(['MEMBER', 'OWNER'])
    def test_valid_for_table(self):
        """It should update the custom properties.
        """
        resource = factories.TableFactory(workspace=self.workspace)
        globalid = helpers.to_global_id('TableType', resource.pk)

        self._test_valid_for_content_type(resource, globalid)

    @decorators.as_someone(['READONLY', 'OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        resource = factories.DatastoreFactory(workspace=self.workspace)
        globalid = helpers.to_global_id('DatastoreType', resource.pk)

        variables = {
            'objectId': globalid,
            'properties': [],
        }

        self.assertPermissionDenied(self.execute(variables=variables))
