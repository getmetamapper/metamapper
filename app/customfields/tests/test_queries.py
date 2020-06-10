# -*- coding: utf-8 -*-
import testutils.cases as cases
import testutils.decorators as decorators
import testutils.factories as factories
import testutils.helpers as helpers

import app.customfields.models as models


class TestGetCustomFieldsByContentType(cases.GraphQLTestCase):
    """Test cases for listing all custom fields for a resource type of a workspace.
    """
    factory = factories.CustomFieldFactory
    operation = 'customFields'
    statement = '''
    query getCustomFields {
      customFields(contentType: "DATASTORE") {
        edges {
          node {
            id
            pk
            fieldName
            fieldType
            validators
          }
        }
        totalCount
      }
    }
    '''

    def setUp(self):
        super(TestGetCustomFieldsByContentType, self).setUp()

        self.content_type = helpers.get_content_type('datastore')
        self.count = 5
        self.customfields = self.factory.create_batch(
            self.count,
            content_type=self.content_type,
            workspace=self.workspace,
        )
        self.excluded_field = self.factory(
            content_type=self.content_type,
            workspace=self.other_workspace,
        )

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement)
        results = results['data'][self.operation]

        self.assertEqual(
            first=len(results['edges']),
            second=self.count,
            msg="Node count should equal number of custom fields."
        )

        self.assertEqual(
            first=len(results['edges']),
            second=results['totalCount'],
            msg="Node count should equal totalCount field."
        )

    @decorators.as_someone(['OUTSIDER'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        self.assertPermissionDenied(self.execute(self.statement))


class TestGetCustomProperties(cases.GraphQLTestCase):
    """Test cases for listing all datastores in a workspace.
    """
    factory = factories.DatastoreFactory
    operation = 'customProperties'
    statement = '''
    query getCustomProperties($objectId: ID!) {
      customProperties(
        objectId: $objectId
      )
    }
    '''

    def setUp(cls):
        super().setUp()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.global_id = helpers.to_global_id('DatastoreType', cls.datastore.pk)

        cls.attributes = {
            'content_type': cls.datastore.content_type,
            'workspace': cls.workspace,
        }

        cls.customfields = [
            factories.CustomFieldFactory(
                field_name='Steward',
                field_type=models.CustomField.USER,
                validators={},
                **cls.attributes,
            ),
            factories.CustomFieldFactory(
                field_name='Product Area',
                field_type=models.CustomField.TEXT,
                validators={},
                **cls.attributes,
            ),
            factories.CustomFieldFactory(
                field_name='Team',
                field_type=models.CustomField.ENUM,
                validators={'choices': ['Data Engineering', 'Product', 'Design']},
                **cls.attributes,
            ),
        ]

        cls.datastore.custom_properties = {
            cls.customfields[0].pk: cls.user.pk,
            cls.customfields[2].pk: 'Design',
        }
        cls.datastore.save()

    @decorators.as_someone(['MEMBER', 'READONLY', 'OWNER'])
    def test_query_when_authorized(self):
        results = self.execute(self.statement, variables={'objectId': self.global_id})
        results = results['data'][self.operation]

        self.assertEqual(results, [
            {
                'fieldId': self.customfields[0].pk,
                'fieldLabel': self.customfields[0].field_name,
                'fieldValue': {
                    'name': 'Sam Crust',
                    'email': 'owner@metamapper.io',
                    'pk': 1,
                    'type': 'User',
                },
            },
            {
                'fieldId': self.customfields[1].pk,
                'fieldLabel': self.customfields[1].field_name,
                'fieldValue': None,
            },
            {
                'fieldId': self.customfields[2].pk,
                'fieldLabel': self.customfields[2].field_name,
                'fieldValue': 'Design',

            },
        ])

    @decorators.as_someone(['OUTSIDER', 'ANONYMOUS'])
    def test_query_when_not_authorized(self):
        """Outside users should not be able to access this resource.
        """
        results = self.execute(self.statement, variables={'objectId': self.global_id})
        self.assertPermissionDenied(results)
