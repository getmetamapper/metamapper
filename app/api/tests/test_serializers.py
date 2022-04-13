# -*- coding: utf-8 -*-
import collections

import app.api.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class ApiTokenSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the ApiTokenSerializer.create method.
    """
    factory = factories.ApiTokenFactory

    serializer_class = serializers.ApiTokenSerializer

    serializer_resource_name = 'ApiToken'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': helpers.faker.company(),
            'is_enabled': True,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    def test_duplicate_name_in_workspace(self):
        """It should throw an error if the validator is not correct.
        """
        token_name = 'Automated Access (Data Lake)'
        token = factories.ApiTokenFactory(name=token_name, workspace=self.workspace)

        attributes = self._get_attributes(name=token.name)
        serializer = self.serializer_class(data=attributes, context={'request': self.request})

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'ApiToken',
                'field': 'name',
                'code': 'exists',
            }
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 85)},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class ApiTokenSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the ApiTokenSerializer.update method.
    """
    factory = factories.ApiTokenFactory

    serializer_class = serializers.ApiTokenSerializer

    serializer_resource_name = 'ApiToken'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)
        cls.instance = cls.factory(
            name='Automated Access (Data Lake)',
            is_enabled=True,
            workspace=cls.workspace,
        )

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'Automated Access (Data Lake)',
            'is_enabled': True,
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to update the resource.
        """
        attributes = {
            'name': 'Bad Dog',
            'is_enabled': False,
        }

        serializer = self.serializer_class(
            instance=self.instance,
            data=attributes,
            partial=True,
            context={'request': self.request},
        )

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save())
        self.assertEqual(
            serializer.instance.is_enabled,
            attributes['is_enabled'],
        )
        self.assertNotEqual(
            serializer.instance.name,
            attributes['name'],
        )

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(65, 85)},
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
        )
