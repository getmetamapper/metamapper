# -*- coding: utf-8 -*-
import app.integrations.serializers as serializers

import testutils.cases as cases
import testutils.factories as factories


class IntegrationConfigSerializerTests(cases.SerializerTestCase):
    """Test cases for the IntegrationConfigSerializer class.
    """
    factory = factories.IntegrationConfigFactory

    serializer_class = serializers.IntegrationConfigSerializer

    serializer_resource_name = 'IntegrationConfig'

    def _get_attributes(self, **overrides):
        """Generate testing data.
        """
        attributes = {
            'integration': 'SLACK',
            'meta': {
                'token': 'xoxb-meowmeowmeow',
                'workspace': 'Acme Corporation',
                'bot_name': 'Robo',
            },
        }
        attributes.update(**overrides)
        return attributes

    def test_when_valid(self):
        """It should not throw an error when the input is valid.
        """
        attributes = self._get_attributes()
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())

    def test_with_extra_meta(self):
        """It should not throw an error when the input is valid.
        """
        meta = {
            'token': 'xoxb-meowmeowmeow',
            'workspace': 'Acme Corporation',
            'bot_name': 'Robo',
            'extra_random': 'nothingness',
        }

        attributes = self._get_attributes(meta=meta)
        serializer = self.serializer_class(data=attributes)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.data, {
            'integration': 'SLACK',
            'meta': {
                'workspace': 'Acme Corporation',
                'bot_name': 'Robo',
                'icon_url': None,
            },
        })

    def test_with_bad_meta(self):
        """It should not throw an error when the input is valid.
        """
        attributes = self._get_attributes(meta={'workspace': 'Acme Corporation'})
        serializer = self.serializer_class(data=attributes)

        self.assertFalse(serializer.is_valid())
        self.assertSerializerErrorsEqual(serializer, [
            {
                'resource': 'IntegrationConfig',
                'field': 'token',
                'code': 'required',
            }
        ])

    def test_drf_validation_rules(self):
        """It should return error messages when DRF validation fails.
        """
        test_case_dict = {
            'integration': [
                {'code': 'invalid_choice', 'value': 'LOTUS'},
            ],
        }

        self.assertDjangoRestFrameworkRules(test_case_dict)
