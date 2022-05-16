# -*- coding: utf-8 -*-
import collections
import datetime as dt

import app.checks.serializers as serializers

import utils.shortcuts as shortcuts

import testutils.cases as cases
import testutils.factories as factories
import testutils.helpers as helpers


class CheckSerializerCreateTests(cases.SerializerTestCase):
    """Test cases for the CheckSerializer.create method.
    """
    factory = factories.CheckFactory

    serializer_class = serializers.CheckSerializer

    serializer_resource_name = 'Check'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.query = factories.CheckQueryFactory(workspace=cls.workspace)
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)
        cls.context = {'request': cls.request, 'datastore': cls.datastore}

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': helpers.faker.company(),
            'is_enabled': True,
            'tags': ['one', 'two'],
            'short_desc': 'the brown fox jumped over the lazy dog',
            'query_id': shortcuts.to_global_id('CheckQueryType', self.query.id),
            'interval': '01:00:00',
            'expectations': [
                {
                    'handler_class': 'app.checks.tasks.expectations.AssertRowCountToBe',
                    'handler_input': {'value': 100, 'op': 'greater than'},
                    'pass_value_class': 'app.checks.tasks.pass_values.Constant',
                    'pass_value_input': {'value': 0},
                }
            ],
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should be able to create the resource.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes, context=self.context)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace, creator=self.workspace.creator))

    def test_when_expectation_invalid(self):
        """It should raise an error if expectation is not valid.
        """
        expectations = [
            {
                'handler_class': 'app.checks.tasks.expectations.AssertRowCountToBe',
                'handler_input': {'value': 100, 'op': 'invalid'},
                'pass_value_class': 'app.checks.tasks.pass_values.Constant',
                'pass_value_input': {'value': 0},
            },

        ]

        attributes = self._get_attributes(expectations=expectations)
        serializer = self.serializer_class(data=attributes, context=self.context)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'Check',
                'field': 'expectations.op',
                'code': 'invalid_choice',
            }
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'name': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'max_length', 'value': helpers.faker.pystr(60, 75)},
            ],
            'is_enabled': [
                {'code': 'nulled', 'value': None},
            ],
            'short_desc': [
                {
                    'code': 'max_length',
                    'value': helpers.faker.pystr(145, 175),
                },
            ],
            'tags': [
                {
                    'code': 'item_max_length',
                    'value': [helpers.faker.pystr(35, 40)],
                },
                {
                    'code': 'max_length',
                    'value': [str(i) for i in range(15)],
                },
            ],
            'query_id': [
                {'code': 'exists', 'value': 'Q2hlY2tRdWVyeVR5cGU6NTEyMzIxMjM='},
            ],
            'interval': [
                {'code': 'invalid', 'value': '01:30:00'},
            ],
            'expectations': [
                {'code': 'empty', 'value': []},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict, context=self.context)


class CheckSerializerUpdateTests(cases.SerializerTestCase):
    """Test cases for the CheckSerializer.update method.
    """
    factory = factories.CheckFactory

    serializer_class = serializers.CheckSerializer

    serializer_resource_name = 'Check'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)
        cls.context = {'request': cls.request, 'datastore': cls.datastore}
        cls.instance = cls.factory(
            name='Automated Data Check',
            is_enabled=True,
            workspace=cls.workspace,
        )

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': 'Automated Data Check V2',
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
            'interval': '00:30:00',
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
        self.assertEqual(
            serializer.instance.name,
            attributes['name'],
        )
        self.assertEqual(
            serializer.instance.interval,
            dt.timedelta(minutes=30),
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
            'is_enabled': [
                {'code': 'nulled', 'value': None},
            ],
            'query_id': [
                {'code': 'exists', 'value': 'Q2hlY2tRdWVyeVR5cGU6NTEyMzIxMjM='},
            ],
            'interval': [
                {'code': 'invalid', 'value': '01:30:00'},
            ],
        }

        self.assertDjangoRestFrameworkRules(
            test_case_dict,
            instance=self.instance,
            partial=True,
            context=self.context,
        )


class CheckQuerySerializerTests(cases.SerializerTestCase):
    """Test cases for the CheckQuerySerializer.
    """
    factory = factories.CheckQueryFactory

    serializer_class = serializers.CheckQuerySerializer

    serializer_resource_name = 'CheckQuery'

    @classmethod
    def setUpTestData(cls):
        cls.workspace = factories.WorkspaceFactory()
        cls.datastore = factories.DatastoreFactory(workspace=cls.workspace)
        cls.request = collections.namedtuple('Request', ['workspace'])(workspace=cls.workspace)
        cls.context = {'request': cls.request, 'datastore': cls.datastore}

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'sql_text': 'SELECT id FROM auth_workspaces WHERE DATE(created_at) = \'{{ ds \'',
            'interval': '01:00:00',
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should not throw an error when the input is valid.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes, context=self.context)

        self.assertTrue(serializer.is_valid())
        self.assertTrue(serializer.save(workspace=self.workspace))

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'sql_text': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'select_only', 'value': 'DELETE FROM auth_workspaces'},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class CheckExpectationSerializerTests(cases.SerializerTestCase):
    """Test cases for the CheckExpectationSerializer.
    """
    factory = factories.CheckExpectationFactory

    serializer_class = serializers.CheckExpectationSerializer

    serializer_resource_name = 'CheckExpectation'

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'handler_class': 'app.checks.tasks.expectations.AssertRowCountToBe',
            'handler_input': {'value': 100, 'op': 'greater than'},
            'pass_value_class': 'app.checks.tasks.pass_values.Constant',
            'pass_value_input': {'value': 0},
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should not throw an error when the input is valid.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'handler_class': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'app.checks.tasks.not_valid.Nope'},
            ],
            'handler_input': [
                {'code': 'nulled', 'value': None},
            ],
            'pass_value_class': [
                {'code': 'nulled', 'value': None},
                {'code': 'blank', 'value': ''},
                {'code': 'invalid', 'value': 'app.checks.tasks.pass_values.DoesNotExist'},
            ],
            'pass_value_input': [
                {'code': 'nulled', 'value': None},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)


class CheckAlertRuleSerializerTests(cases.SerializerTestCase):
    """Test cases for the CheckAlertRuleSerializer class.
    """
    factory = factories.CheckAlertRuleFactory

    serializer_class = serializers.CheckAlertRuleSerializer

    serializer_resource_name = 'CheckAlertRule'

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'name': helpers.faker.name(),
            'interval': '1:00:00',
            'channel': 'EMAIL',
            'channel_config': {'emails': ['test1@metamapper.io', 'test2@metamapper.io']}
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should not throw an error when the input is valid.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

    def test_with_extra_channel_config(self):
        """It should not throw an error when the input is valid.
        """
        channel_config = {
            'emails': ['scott.test@metamapper.io'],
        }

        attributes = self._get_attributes(channel_config=channel_config)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

    def test_with_bad_channel_config(self):
        """It should not throw an error when the input is valid.
        """
        channel_config = {
            'emails': ['scott.test'],
        }

        attributes = self._get_attributes(channel_config=channel_config)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'CheckAlertRule',
                'field': 'emails',
                'code': 'item_invalid',
            }
        ])

    def test_with_empty_channel_config(self):
        """It should not throw an error when the input is valid.
        """
        channel_config = {
            'emails': [],
        }

        attributes = self._get_attributes(channel_config=channel_config)
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'CheckAlertRule',
                'field': 'emails',
                'code': 'empty',
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
            'interval': [
                {'code': 'invalid', 'value': '01:30:00'},
            ],
            'channel': [
                {'code': 'invalid_choice', 'value': 'SMS'},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)
