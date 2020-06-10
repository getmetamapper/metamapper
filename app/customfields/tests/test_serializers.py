# -*- coding: utf-8 -*-
import collections

import app.customfields.models as models
import app.customfields.serializers as serializers

import app.audit.models as audit
import app.authorization.models as auth

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class CustomFieldSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the CustomFieldSerializer.create method.
    """
    factory = factories.CustomFieldFactory

    serializer_class = serializers.CustomFieldSerializer

    serializer_resource_name = 'CustomField'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        content_type = models.CustomField.get_content_type_from_name('datastore')
        attributes = {
            'field_name': 'Team',
            'field_type': models.CustomField.TEXT,
            'content_type': content_type,
            'validators': {
                'extras': '',
            },
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))
        self.assertFalse(serializer.instance.validators)

    def test_invalid_enum_nulled(self):
        """It should throw an error if the validator is not correct.
        """
        attributes = self._get_attributes(
            field_type=models.CustomField.ENUM,
            validators={},
        )

        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'CustomField',
                'field': 'choices',
                'code': 'required',
            }
        ])

    def test_invalid_enum_empty(self):
        """It should throw an error if the validator is not correct.
        """
        attributes = self._get_attributes(
            field_type=models.CustomField.ENUM,
            validators={'choices': []},
        )

        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'CustomField',
                'field': 'choices',
                'code': 'empty',
            }
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'field_name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(35, 45)},
            ],
            'field_type': [
                {'code': 'nulled', 'value': None},
                {'code': 'invalid_choice', 'value': ''},
                {'code': 'invalid_choice', 'value': 'not-a-choice'},
            ],
            'short_desc': [
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'content_type': [
                {'code': 'nulled', 'value': None},
            ],
            'validators': [
                {'code': 'nulled', 'value': None},
            ]
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class CustomFieldSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the CustomFieldSerializer.update method.
    """
    factory = factories.CustomFieldFactory

    serializer_class = serializers.CustomFieldSerializer

    serializer_resource_name = 'CustomField'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.instance = cls.factory(
            field_type=models.CustomField.TEXT,
            workspace=cls.workspace,
        )

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'field_name': helpers.faker.company(),
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = {
            'field_name': 'Product Area',
            'field_type': models.CustomField.ENUM,
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertEqual(
            serializer.instance.field_type,
            models.CustomField.TEXT,
        )
        self.assertEqual(
            serializer.instance.field_name,
            attributes['field_name'],
        )

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'field_name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(35, 45)},
            ],
            'field_type': [
                {'code': 'nulled', 'value': None},
                {'code': 'invalid_choice', 'value': ''},
                {'code': 'invalid_choice', 'value': 'not-a-choice'},
            ],
            'short_desc': [
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 80)},
            ],
            'content_type': [
                {'code': 'nulled', 'value': None},
            ]
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )


class CustomPropertiesSerializerTests(cases.SerializerTestCase):
    """Test cases for the CustomPropertiesSerializer.update method.
    """
    factory = None

    serializer_class = serializers.CustomPropertiesSerializer

    @classmethod
    def setUpTestData(cls):
        cls.current_user = factories.UserFactory()
        cls.workspace = factories.WorkspaceFactory(creator=cls.current_user)
        cls.workspace.grant_membership(cls.current_user, auth.Membership.OWNER)
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
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
        cls.request = collections.namedtuple(
            'Request',
            ['user', 'workspace'],
        )(user=cls.current_user, workspace=cls.workspace)

    def test_when_valid(self):
        """It should be able to update the custom properties.
        """
        new_values = {
            'properties': {
                self.customfields[1].pk: 'Data',
                self.customfields[2].pk: 'Product',
            },
        }

        serializer = self.serializer_class(
            instance=self.datastore,
            data=new_values,
            partial=True,
            context={'request': self.request},
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

        activity = audit.Activity.objects.get(extras__datastore_id=self.datastore.id)

        self.assertEqual(activity.verb, 'updated custom properties on')
        self.assertEqual(activity.actor, self.current_user)
        self.assertEqual(activity.old_values, {'custom_properties': {}})
        self.assertEqual(activity.new_values, {'custom_properties': new_values['properties']})

    def test_when_valid_user_change(self):
        """It should be able to update the custom properties.
        """
        new_values = {
            'properties': {
                self.customfields[0].pk: self.current_user.pk,
                self.customfields[1].pk: 'Data',
                self.customfields[2].pk: 'Product',
            },
        }

        serializer = self.serializer_class(
            instance=self.datastore,
            data=new_values,
            partial=True,
            context={'request': self.request},
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())

    def test_when_invalid_property(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.datastore,
            data={'properties': {'Extra Property': 'Test'}},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'CustomField', 'field': 'properties', 'code': 'invalid'}
        ])

    def test_user_exists(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.datastore,
            data={
                'properties': {
                    self.customfields[0].pk: '1234',
                    self.customfields[2].pk: 'test',
                }
            },
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'CustomField', 'field': 'properties', 'code': 'invalid'}
        ])

    def test_enum_field(self):
        """It should be able to create the resource.
        """
        serializer = self.serializer_class(
            instance=self.datastore,
            data={'properties': {self.customfields[2].pk: 'Test'}},
            partial=True,
        )

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {'resource': 'CustomField', 'field': 'properties', 'code': 'invalid'}
        ])
